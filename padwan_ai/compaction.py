from collections.abc import Collection, Sequence
from dataclasses import dataclass
from typing import Protocol, cast

from .conversation import AssistantToolMessage, ChatMessage, ToolResultMessage

__all__ = (
    "CompactionError",
    "Compactor",
    "ElideToolResults",
)

_STUB_PREFIX = "[elided: "


class CompactionError(ValueError):
    """A compactor returned history whose tool calls and results no longer pair up."""


class Compactor(Protocol):
    """Rewrites the older part of a conversation into fewer tokens.

    `messages` is what the model currently sees before the rounds kept whole
    (system prompt excluded); the returned list replaces it in every request
    until the next compaction.
    """

    async def compact(self, messages: Sequence[ChatMessage]) -> list[ChatMessage]: ...


@dataclass(frozen=True)
class ElideToolResults:
    """Replace old tool results with a short stub; results of tools named in `keep` stay whole."""

    keep: Collection[str] = ()

    async def compact(self, messages: Sequence[ChatMessage]) -> list[ChatMessage]:
        out: list[ChatMessage] = []
        for msg in messages:
            if (
                msg["role"] == "tool"
                and (result := cast(ToolResultMessage, msg))["name"] not in self.keep
            ):
                stub = f"{_STUB_PREFIX}{len(result['content'])} chars of {result['name']} result]"
                # a later compaction gets earlier stubs back; keep their original size
                if len(result["content"]) > len(stub) and not result[
                    "content"
                ].startswith(_STUB_PREFIX):
                    msg = ToolResultMessage(
                        role="tool",
                        tool_call_id=result["tool_call_id"],
                        name=result["name"],
                        content=stub,
                    )
            out.append(msg)
        return out


def _check_pairs(messages: Sequence[ChatMessage]) -> None:
    """Raise `CompactionError` unless every tool call has its result and every result its call."""
    calls: set[str] = set()
    results: set[str] = set()
    for msg in messages:
        if msg["role"] == "tool":
            call_id = cast(ToolResultMessage, msg)["tool_call_id"]
            if call_id not in calls:
                raise CompactionError(f"tool result {call_id!r} has no earlier call")
            results.add(call_id)
        elif tool_calls := cast(AssistantToolMessage, msg).get("tool_calls"):
            calls.update(tc["id"] for tc in tool_calls)
    if missing := calls - results:
        raise CompactionError(f"tool calls without a result: {sorted(missing)}")


def _round_start(messages: Sequence[ChatMessage], keep_rounds: int) -> int | None:
    """Index of the first message of the last `keep_rounds` rounds, or None if there are no more."""
    starts = [i for i, msg in enumerate(messages) if msg["role"] == "assistant"]
    if len(starts) <= keep_rounds:
        return None
    return starts[-keep_rounds] if keep_rounds else len(messages)
