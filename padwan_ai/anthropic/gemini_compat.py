from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, cast

from .._json import dumps as _json_dumps, loads as _json_loads
from ..gemini.models import (
    CompletionBody,
    FunctionCallPart,
    FunctionDeclaration,
    GeminiPart,
    GeminiTool,
    InlineDataPart,
    Part,
    SystemInstruction,
    ToolConfig,
)
from ..logs import log
from .events import _BlockEmitter, _new_message_id
from .models import (
    AnthropicCompatBody,
    AnthropicContentBlock,
    AnthropicTool,
    AnthropicToolChoice,
    StopReason,
)

if TYPE_CHECKING:
    from google.genai.types import GenerateContentResponseDict

__all__ = (
    "gemini_response_to_anthropic",
    "gemini_stream_to_anthropic",
    "messages_to_gemini",
)

# Gemini finish reasons mapped to Anthropic stop reasons.
# https://ai.google.dev/api/generate-content#FinishReason
_GEMINI_TO_STOP: dict[str, StopReason] = {
    "STOP": "end_turn",
    "MAX_TOKENS": "max_tokens",
    "SAFETY": "refusal",
    "RECITATION": "refusal",
    "LANGUAGE": "refusal",
    "BLOCKLIST": "refusal",
    "PROHIBITED_CONTENT": "refusal",
    "SPII": "refusal",
    "OTHER": "end_turn",
}


def _system_text(system: str | list[AnthropicContentBlock]) -> str | None:
    """Flatten a system prompt (string or text blocks) to a single string."""
    if isinstance(system, str):
        return system or None
    parts = [t for b in system if b.get("type") == "text" and (t := b.get("text"))]
    return "\n\n".join(parts) or None


def _image_source_to_inline_data(
    source: dict[str, Any],
) -> InlineDataPart | None:
    """Convert an Anthropic image `source` to a Gemini `inlineData` part."""
    match source.get("type"):
        case "base64":
            mime_type = source.get("media_type", "image/png")
            data = source.get("data", "")
            return {"inlineData": {"mimeType": mime_type, "data": data}}
        case "url":
            log.debug("anthropic compat: Gemini drops remote image URLs %r", source.get("url"))
            return None
        case unknown:
            log.debug("anthropic compat: skipping image source type %r", unknown)
            return None


def _flatten_tool_result_content(content: Any) -> dict[str, Any]:
    """Flatten a tool_result `content` to a JSON-able Gemini function response payload."""
    if content is None:
        return {}
    if isinstance(content, str):
        return _maybe_json(content)
    if isinstance(content, list):
        texts = [
            b["text"]
            for b in content
            if isinstance(b, dict) and b.get("type") == "text" and b.get("text")
        ]
        return _maybe_json("\n".join(texts)) if texts else {}
    return {"result": str(content)}


def _maybe_json(text: str) -> dict[str, Any]:
    """Parse JSON if `text` is an object, else wrap in {"result": text}."""
    try:
        parsed = _json_loads(text)
    except (ValueError, TypeError):
        return {"result": text}
    return parsed if isinstance(parsed, dict) else {"result": parsed}


def _user_blocks_to_content(blocks: list[AnthropicContentBlock]) -> list[dict[str, Any]]:
    """Convert a user message's content blocks to Gemini Content entries.

    tool_result blocks each become a `role: "user"` functionResponse content;
    contiguous text/image blocks become a `role: "user"` content with parts.
    """
    contents: list[dict[str, Any]] = []
    parts: list[GeminiPart] = []

    def flush_parts() -> None:
        if not parts:
            return
        contents.append({"role": "user", "parts": list(parts)})
        parts.clear()

    for block in blocks:
        match block.get("type"):
            case "text":
                if text := block.get("text"):
                    parts.append(Part(text=text))
            case "image":
                if part := _image_source_to_inline_data(block.get("source") or {}):
                    parts.append(part)
            case "tool_result":
                flush_parts()
                response = _flatten_tool_result_content(block.get("content"))
                contents.append(
                    {
                        "role": "user",
                        "parts": [
                            {
                                "functionResponse": {
                                    "name": block.get("tool_use_id", ""),
                                    "response": response,
                                }
                            }
                        ],
                    }
                )
            case unknown:
                log.debug("anthropic compat: skipping user block type %r", unknown)
    flush_parts()
    return contents


def _assistant_blocks_to_content(blocks: list[AnthropicContentBlock]) -> dict[str, Any]:
    """Convert an assistant message's content blocks to one Gemini `model` content."""
    parts: list[GeminiPart] = []
    for block in blocks:
        match block.get("type"):
            case "text":
                if text := block.get("text"):
                    parts.append(Part(text=text))
            case "tool_use":
                part: FunctionCallPart = {
                    "functionCall": {
                        "name": block.get("name", ""),
                        "args": block.get("input") or {},
                        "id": block.get("id", ""),
                    }
                }
                parts.append(part)
            case "thinking" | "redacted_thinking":
                log.debug("anthropic compat: dropping thinking block on replay")
            case unknown:
                log.debug("anthropic compat: skipping assistant block type %r", unknown)
    return {"role": "model", "parts": parts or [Part(text="")]}


def _tools_to_gemini(tools: list[AnthropicTool]) -> list[GeminiTool]:
    """Convert Anthropic tool definitions, skipping server tools (no input_schema)."""
    declarations: list[FunctionDeclaration] = []
    for tool in tools:
        if (schema := tool.get("input_schema")) is None:
            log.debug(
                "anthropic compat: skipping server tool %r (type=%r)",
                tool.get("name"),
                tool.get("type"),
            )
            continue
        declarations.append(
            {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": schema,
            }
        )
    return [{"function_declarations": declarations}] if declarations else []


def _tool_config(tool_choice: AnthropicToolChoice) -> ToolConfig:
    """Map Anthropic tool_choice to Gemini's functionCallingConfig."""
    mode = "ANY" if tool_choice["type"] in ("any", "tool") else tool_choice["type"].upper()
    config: ToolConfig = {"function_calling_config": {"mode": cast("Any", mode)}}
    if tool_choice["type"] == "tool":
        config["function_calling_config"]["allowed_function_names"] = [tool_choice.get("name", "")]
    return config


def messages_to_gemini(
    body: AnthropicCompatBody, *, model: str | None = None
) -> CompletionBody:
    """Translate an Anthropic Messages API request to a Gemini generateContent body.

    `model` overrides the requested (Anthropic) model name with the backend
    model to use; when omitted the original name is kept. `cache_control`
    markers, `metadata`, and the `thinking` config are dropped; thinking blocks
    are stripped from replayed assistant turns (their signatures only make
    sense to the Anthropic API).
    """
    contents: list[dict[str, Any]] = []
    for msg in body["messages"]:
        content = msg["content"]
        if msg["role"] == "assistant":
            if isinstance(content, str):
                contents.append({"role": "model", "parts": [Part(text=content)]})
            else:
                contents.append(_assistant_blocks_to_content(content))
        elif isinstance(content, str):
            contents.append({"role": "user", "parts": [Part(text=content)]})
        else:
            contents.extend(_user_blocks_to_content(content))

    gen_config: dict[str, Any] = {"maxOutputTokens": body["max_tokens"]}
    if (temperature := body.get("temperature")) is not None:
        gen_config["temperature"] = temperature
    if (top_p := body.get("top_p")) is not None:
        gen_config["topP"] = top_p
    if (top_k := body.get("top_k")) is not None:
        gen_config["topK"] = top_k
    if stop_sequences := body.get("stop_sequences"):
        gen_config["stopSequences"] = stop_sequences

    request: dict[str, Any] = {"contents": contents, "generationConfig": gen_config}
    if (system := body.get("system")) is not None:
        if text := _system_text(system):
            request["systemInstruction"] = SystemInstruction(parts=[Part(text=text)])
    if tools := _tools_to_gemini(body.get("tools") or []):
        request["tools"] = tools
    if (tool_choice := body.get("tool_choice")) and "tools" in request:
        request["toolConfig"] = _tool_config(tool_choice)
    if body.get("thinking"):
        log.debug("anthropic compat: dropping thinking config (backend-specific)")
    # Carry the resolved model; complete()/stream() also accept it explicitly.
    request["model"] = model or body["model"]
    return cast(CompletionBody, request)


def _parts_to_blocks(parts: list[dict[str, Any]]) -> list[AnthropicContentBlock]:
    """Convert Gemini response parts to Anthropic content blocks, in order."""
    blocks: list[AnthropicContentBlock] = []
    for i, part in enumerate(parts):
        if part.get("thought"):
            if thought_text := part.get("text"):
                blocks.append({"type": "thinking", "thinking": thought_text})
            continue
        if (text := part.get("text")) is not None:
            blocks.append({"type": "text", "text": text})
            continue
        if fc := part.get("functionCall"):
            blocks.append(
                {
                    "type": "tool_use",
                    "id": fc.get("id") or f"call_{i}",
                    "name": fc.get("name", ""),
                    "input": fc.get("args") or {},
                }
            )
    return blocks


def _usage_to_anthropic(usage: dict[str, Any] | None) -> dict[str, Any]:
    if not usage:
        return {"input_tokens": 0, "output_tokens": 0}
    token: dict[str, Any] = {
        "input_tokens": usage.get("promptTokenCount", 0),
        "output_tokens": usage.get("candidatesTokenCount", 0),
    }
    if (cached := usage.get("cachedContentTokenCount")) is not None:
        token["cache_read_input_tokens"] = cached
    return token


def gemini_response_to_anthropic(
    data: GenerateContentResponseDict, *, model: str | None = None
) -> dict[str, Any]:
    """Translate a Gemini generateContent response to an Anthropic Messages response."""
    candidates = data.get("candidates") or []
    blocks: list[AnthropicContentBlock] = []
    saw_tool_call = False
    raw_reason = "STOP"
    if candidates:
        choice = candidates[0]
        content = choice.get("content") or {}
        parts = cast(list[dict[str, Any]], content.get("parts") or [])
        blocks = _parts_to_blocks(parts)
        saw_tool_call = any(b.get("type") == "tool_use" for b in blocks)
        raw_reason = choice.get("finishReason") or "STOP"
    stop_reason: StopReason = (
        "tool_use"
        if saw_tool_call
        else _GEMINI_TO_STOP.get(raw_reason, "end_turn")
    )
    return {
        "id": data.get("id") or _new_message_id(),
        "type": "message",
        "role": "assistant",
        "model": model or data.get("model", ""),
        "content": blocks,
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": _usage_to_anthropic(data.get("usageMetadata")),
    }


async def gemini_stream_to_anthropic(
    chunks: AsyncIterator[dict], *, model: str
) -> AsyncIterator[tuple[str, dict[str, Any]]]:
    """Translate a Gemini streamGenerateContent stream to Anthropic SSE events.

    Gemini emits whole parts per chunk (a text part, a functionCall part),
    not token deltas — each part becomes a content block opened, fed once,
    and closed on the next block kind. Yields (event name, payload) pairs
    following the Messages API sequence.
    """
    yield (
        "message_start",
        {
            "type": "message_start",
            "message": {
                "id": _new_message_id(),
                "type": "message",
                "role": "assistant",
                "model": model,
                "content": [],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {"input_tokens": 0, "output_tokens": 0},
            },
        },
    )

    emitter = _BlockEmitter()
    # "thinking" | "text" | open index of the tool_use block currently open.
    open_kind: str | int | None = None
    finish_reason: str | None = None
    usage: dict[str, Any] | None = None
    saw_tool_call = False
    tool_index = 0

    async for chunk in chunks:
        if chunk_usage := chunk.get("usageMetadata"):
            usage = chunk_usage
        candidates = chunk.get("candidates") or []
        if not candidates:
            continue
        choice = candidates[0]
        if reason := choice.get("finishReason"):
            finish_reason = reason
        content = choice.get("content") or {}
        parts = content.get("parts") or []

        for part in parts:
            if part.get("thought"):
                if thought_text := part.get("text"):
                    if open_kind != "thinking":
                        open_kind = "thinking"
                        for event in emitter.open({"type": "thinking", "thinking": ""}):
                            yield event
                    yield emitter.delta({"type": "thinking_delta", "thinking": thought_text})
                continue
            if (text := part.get("text")) is not None:
                if open_kind != "text":
                    open_kind = "text"
                    for event in emitter.open({"type": "text", "text": ""}):
                        yield event
                yield emitter.delta({"type": "text_delta", "text": text})
                continue
            if fc := part.get("functionCall"):
                saw_tool_call = True
                idx = tool_index
                tool_index += 1
                if open_kind != idx:
                    open_kind = idx
                    for event in emitter.open(
                        {
                            "type": "tool_use",
                            "id": fc.get("id") or f"call_{idx}",
                            "name": fc.get("name", ""),
                            "input": {},
                        }
                    ):
                        yield event
                # Gemini returns whole args; emit them as one JSON delta.
                yield emitter.delta(
                    {
                        "type": "input_json_delta",
                        "partial_json": _json_dumps(fc.get("args") or {}),
                    }
                )

    for event in emitter.close():
        yield event

    stop_reason: StopReason = (
        "tool_use"
        if saw_tool_call
        else _GEMINI_TO_STOP.get(finish_reason or "STOP", "end_turn")
    )
    yield (
        "message_delta",
        {
            "type": "message_delta",
            "delta": {"stop_reason": stop_reason, "stop_sequence": None},
            "usage": _usage_to_anthropic(usage),
        },
    )
    yield ("message_stop", {"type": "message_stop"})
