import copy
import json
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass, field
from typing import Any, Self

from ._base import ChatStream
from .conversation import ChatMessage
from .models import ChatResponse, ToolCall, ToolCallFunction, ToolDefinition, UsageToken

__all__ = ("Request", "ScriptedClient", "Step")


def _default_usage() -> UsageToken:
    return {"total": 10, "input": 7, "output": 3}


@dataclass
class Step:
    """One scripted round: what the model says and/or the `(tool_name, arguments)` it calls."""

    text: str | None = None
    tool_calls: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    usage: UsageToken = field(default_factory=_default_usage)


@dataclass
class Request:
    """Snapshot of what one round sent to the model."""

    messages: list[ChatMessage]
    tools: list[ToolDefinition]
    extra_params: dict[str, Any] | None = None

    @property
    def tool_names(self) -> list[str]:
        return [t["name"] for t in self.tools]


class _ScriptedStream(ChatStream):
    def __init__(self, step: Step, round_no: int) -> None:
        self._step = step
        self._round = round_no

    async def __aiter__(self) -> AsyncIterator[str]:
        if self._step.text is not None:
            yield self._step.text
        self.usage = self._step.usage
        self.tool_calls = _tool_calls(self._step, self._round)


def _tool_calls(step: Step, round_no: int) -> list[ToolCall] | None:
    calls = [
        ToolCall(
            id=f"call_{round_no}_{i}",
            type="function",
            function=ToolCallFunction(name=name, arguments=json.dumps(args)),
        )
        for i, (name, args) in enumerate(step.tool_calls)
    ]
    return calls or None


class ScriptedClient:
    """Client stand-in that replays `Step`s in order and records each round's request.

    Raises `AssertionError` when asked for more rounds than scripted.
    """

    def __init__(self, steps: Sequence[Step]) -> None:
        self._steps = list(steps)
        self.requests: list[Request] = []
        self._is_open = False

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def remaining(self) -> int:
        """Steps not consumed yet; assert 0 to prove the whole script ran."""
        return len(self._steps)

    async def __aenter__(self) -> Self:
        self._is_open = True
        return self

    async def __aexit__(self, *_: object) -> None:
        self._is_open = False

    def _next(
        self,
        messages: Sequence[ChatMessage],
        tools: Sequence[ToolDefinition] | None,
        extra_params: dict[str, Any] | None,
    ) -> tuple[Step, int]:
        if not self._steps:
            raise AssertionError(
                f"ScriptedClient: script exhausted after {len(self.requests)} round(s)"
            )
        # deepcopy: callers mutate messages between rounds, the record must not follow
        self.requests.append(
            Request(
                copy.deepcopy(list(messages)),
                copy.deepcopy(list(tools or [])),
                copy.deepcopy(extra_params),
            )
        )
        return self._steps.pop(0), len(self.requests)

    def stream_chat(
        self,
        messages: Sequence[ChatMessage],
        tools: Sequence[ToolDefinition] | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> ChatStream:
        step, round_no = self._next(messages, tools, extra_params)
        return _ScriptedStream(step, round_no)

    async def complete_chat(
        self,
        messages: Sequence[ChatMessage],
        tools: Sequence[ToolDefinition] | None = None,
    ) -> tuple[ChatResponse, UsageToken]:
        step, round_no = self._next(messages, tools, None)
        calls = _tool_calls(step, round_no)
        response: ChatResponse = {
            "content": step.text,
            "finish_reason": "tool_calls" if calls else "stop",
        }
        if calls:
            response["tool_calls"] = calls
        return response, step.usage
