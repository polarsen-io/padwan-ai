import json
from contextlib import nullcontext
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import AsyncMock

import pytest

from padwan_ai.anthropic.gemini_compat import (
    gemini_response_to_anthropic,
    gemini_stream_to_anthropic,
    messages_to_gemini,
)
from padwan_ai.anthropic.models import AnthropicCompatBody
from padwan_ai.gemini.client import GeminiClient

if TYPE_CHECKING:
    from google.genai.types import GenerateContentResponseDict

BASE64_PNG = "iVBORw0KGgo="


def _body(**overrides) -> AnthropicCompatBody:
    body: AnthropicCompatBody = {
        "model": "claude-sonnet-5",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": "hello"}],
    }
    body.update(cast(Any, overrides))
    return body


def _to_gemini(
    body: AnthropicCompatBody, *, model: str | None = None
) -> dict[str, Any]:
    return cast("dict[str, Any]", messages_to_gemini(body, model=model))


# messages_to_gemini


@pytest.mark.parametrize(
    "model, expected",
    [
        pytest.param(None, "claude-sonnet-5", id="kept"),
        pytest.param("gemini-2.5-flash", "gemini-2.5-flash", id="overridden"),
    ],
)
def test_model_and_plain_text_content(model, expected):
    request = _to_gemini(_body(), model=model)
    assert request["model"] == expected
    assert request["contents"] == [{"role": "user", "parts": [{"text": "hello"}]}]


@pytest.mark.parametrize(
    "overrides, expected",
    [
        pytest.param({}, {"maxOutputTokens": 1024}, id="max_tokens_only"),
        pytest.param(
            {"temperature": 0.7, "top_p": 0.9, "top_k": 40, "stop_sequences": ["END"]},
            {
                "maxOutputTokens": 1024,
                "temperature": 0.7,
                "topP": 0.9,
                "topK": 40,
                "stopSequences": ["END"],
            },
            id="sampling",
        ),
    ],
)
def test_generation_config(overrides, expected):
    request = _to_gemini(_body(**overrides))
    assert request["generationConfig"] == expected


@pytest.mark.parametrize(
    "system, expected",
    [
        pytest.param("You are helpful.", "You are helpful.", id="string"),
        pytest.param(
            [
                {"type": "text", "text": "You are Claude Code."},
                {
                    "type": "text",
                    "text": "Extra context.",
                    "cache_control": {"type": "ephemeral"},
                },
            ],
            "You are Claude Code.\n\nExtra context.",
            id="blocks_with_cache_control",
        ),
        pytest.param("", None, id="empty_omitted"),
    ],
)
def test_system_maps_to_system_instruction(system, expected):
    request = _to_gemini(_body(system=system))
    if expected is None:
        assert "systemInstruction" not in request
    else:
        assert request["systemInstruction"] == {"parts": [{"text": expected}]}


PNG_SOURCE = {"type": "base64", "media_type": "image/png", "data": BASE64_PNG}
PNG_PART = {"inlineData": {"mimeType": "image/png", "data": BASE64_PNG}}
PDF_SOURCE = {"type": "base64", "media_type": "application/pdf", "data": "JVBERi0="}
PDF_PART = {"inlineData": {"mimeType": "application/pdf", "data": "JVBERi0="}}


def _weather_response(response: dict[str, Any]) -> dict[str, Any]:
    return {
        "functionResponse": {
            "id": "call_1",
            "name": "get_weather",
            "response": response,
        }
    }


def _tool_result(content: Any, **extra: Any) -> dict[str, Any]:
    return {"type": "tool_result", "tool_use_id": "call_1", "content": content, **extra}


@pytest.mark.parametrize(
    "blocks, expected",
    [
        pytest.param(
            [
                {"type": "text", "text": "describe this"},
                {"type": "image", "source": PNG_SOURCE},
            ],
            [{"text": "describe this"}, PNG_PART],
            id="image",
        ),
        pytest.param(
            [{"type": "document", "source": PDF_SOURCE}],
            [PDF_PART],
            id="pdf_document",
        ),
        pytest.param(
            [{"type": "document", "source": {"type": "text", "data": "plain doc"}}],
            [{"text": "plain doc"}],
            id="text_document",
        ),
        pytest.param(
            [_tool_result('{"temp": 18}')],
            [_weather_response({"temp": 18})],
            id="tool_result_json",
        ),
        pytest.param(
            [_tool_result([{"type": "text", "text": "city not found"}], is_error=True)],
            [_weather_response({"error": "city not found"})],
            id="tool_result_error",
        ),
        pytest.param(
            [
                _tool_result(
                    [
                        {"type": "text", "text": "chart"},
                        {"type": "image", "source": PNG_SOURCE},
                    ]
                ),
                {"type": "text", "text": "what does it show?"},
            ],
            [
                _weather_response({"result": "chart"}),
                PNG_PART,
                {"text": "what does it show?"},
            ],
            id="tool_result_image_follows_response",
        ),
    ],
)
def test_user_blocks_to_parts(blocks, expected):
    body = _body(
        messages=[
            {"role": "user", "content": "weather?"},
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "call_1",
                        "name": "get_weather",
                        "input": {},
                    }
                ],
            },
            {"role": "user", "content": blocks},
        ]
    )
    request = _to_gemini(body, model="gemini-2.5-flash")
    assert request["contents"][-1] == {"role": "user", "parts": expected}


@pytest.mark.parametrize(
    "block",
    [
        pytest.param(
            {"type": "image", "source": {"type": "url", "url": "https://x/y.png"}},
            id="remote_image",
        ),
        pytest.param({"type": "search_result"}, id="unknown_block"),
    ],
)
def test_unsupported_user_block_warns(block, caplog):
    with caplog.at_level("WARNING", logger="padwan_ai"):
        request = _to_gemini(_body(messages=[{"role": "user", "content": [block]}]))
    assert request["contents"] == []
    assert any("anthropic compat" in rec.message for rec in caplog.records)


@pytest.mark.parametrize(
    "blocks, expected",
    [
        pytest.param(
            [
                {
                    "type": "tool_use",
                    "id": "call_1",
                    "name": "get_weather",
                    "input": {"city": "Paris"},
                }
            ],
            [
                {
                    "role": "model",
                    "parts": [
                        {
                            "functionCall": {
                                "name": "get_weather",
                                "args": {"city": "Paris"},
                                "id": "call_1",
                            }
                        }
                    ],
                }
            ],
            id="tool_use",
        ),
        pytest.param(
            [
                {"type": "thinking", "thinking": "reasoning here"},
                {"type": "text", "text": "answer"},
            ],
            [{"role": "model", "parts": [{"text": "answer"}]}],
            id="thinking_dropped",
        ),
        pytest.param(
            [
                {"type": "thinking", "thinking": "reasoning here"},
                {"type": "redacted_thinking"},
            ],
            [],
            id="thinking_only_turn_omitted",
        ),
    ],
)
def test_assistant_blocks_to_content(blocks, expected):
    body = _body(messages=[{"role": "assistant", "content": blocks}])
    assert _to_gemini(body)["contents"] == expected


def test_tools_map_to_function_declarations():
    """Schemas go through parametersJsonSchema untouched: Gemini's `parameters`
    rejected Claude Code's `$schema` and `additionalProperties` with a 400."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "additionalProperties": False,
    }
    body = _body(
        tools=[
            {
                "name": "get_weather",
                "description": "Get the weather",
                "input_schema": schema,
            }
        ]
    )
    request = _to_gemini(body, model="gemini-2.5-flash")
    assert request["tools"] == [
        {
            "function_declarations": [
                {
                    "name": "get_weather",
                    "description": "Get the weather",
                    "parametersJsonSchema": schema,
                }
            ]
        }
    ]


@pytest.mark.parametrize(
    "tool_choice, expected",
    [
        pytest.param({"type": "auto"}, {"mode": "AUTO"}, id="auto"),
        pytest.param({"type": "any"}, {"mode": "ANY"}, id="any"),
        pytest.param({"type": "none"}, {"mode": "NONE"}, id="none"),
        pytest.param(
            {"type": "tool", "name": "get_weather"},
            {"mode": "ANY", "allowed_function_names": ["get_weather"]},
            id="specific_tool",
        ),
    ],
)
def test_tool_choice_maps_to_function_calling_config(tool_choice, expected):
    body = _body(
        tools=[
            {
                "name": "get_weather",
                "description": "weather",
                "input_schema": {"type": "object", "properties": {}},
            }
        ]
    )
    body["tool_choice"] = cast(Any, tool_choice)
    request = _to_gemini(body, model="gemini-2.5-flash")
    assert request["toolConfig"] == {"function_calling_config": expected}


# gemini_response_to_anthropic / gemini_stream_to_anthropic


USAGE_META = {
    "promptTokenCount": 100,
    "candidatesTokenCount": 20,
    "totalTokenCount": 120,
    "cachedContentTokenCount": 60,
}


def _completion(parts, finish_reason="STOP", usage=USAGE_META):
    return {
        "candidates": [{"content": {"parts": parts}, "finishReason": finish_reason}],
        "usageMetadata": usage,
    }


def _to_anthropic(data: dict, *, model: str | None = None) -> dict[str, Any]:
    typed = cast("GenerateContentResponseDict", data)
    return cast("dict[str, Any]", gemini_response_to_anthropic(typed, model=model))


def _chunk(parts=None, finish_reason=None, usage=None):
    chunk: dict[str, Any] = {"candidates": []}
    if parts is not None or finish_reason is not None:
        content = {"parts": parts} if parts is not None else {}
        chunk["candidates"] = [{"content": content, "finishReason": finish_reason}]
    if usage is not None:
        chunk["usageMetadata"] = usage
    return chunk


async def _stream(chunks):
    for chunk in chunks:
        yield chunk


async def _collect(chunks, model="claude-sonnet-5"):
    return [
        event
        async for event in gemini_stream_to_anthropic(_stream(chunks), model=model)
    ]


async def _response_blocks(parts, *, stream: bool) -> list[dict[str, Any]]:
    """Content blocks from either translator; stream deltas are folded back in."""
    if not stream:
        return _to_anthropic(_completion(parts))["content"]
    blocks: list[dict[str, Any]] = []
    for name, event in await _collect([_chunk(parts=parts)]):
        if name == "content_block_start":
            blocks.append(event["content_block"].copy())
        elif name == "content_block_delta":
            match event["delta"]:
                case {"type": "text_delta", "text": text}:
                    blocks[-1]["text"] += text
                case {"type": "thinking_delta", "thinking": thinking}:
                    blocks[-1]["thinking"] += thinking
                case {"type": "input_json_delta", "partial_json": partial}:
                    blocks[-1]["input"] = json.loads(partial)
    return blocks


@pytest.mark.parametrize(
    "stream", [pytest.param(False, id="complete"), pytest.param(True, id="stream")]
)
@pytest.mark.parametrize(
    "parts, expected",
    [
        pytest.param(
            [{"text": "Hello!"}], [{"type": "text", "text": "Hello!"}], id="text"
        ),
        pytest.param(
            [
                {
                    "functionCall": {
                        "name": "get_weather",
                        "args": {"city": "Paris"},
                        "id": "call_9",
                    }
                }
            ],
            [
                {
                    "type": "tool_use",
                    "id": "call_9",
                    "name": "get_weather",
                    "input": {"city": "Paris"},
                }
            ],
            id="tool_use",
        ),
        pytest.param(
            [{"functionCall": {"name": "get_weather", "args": {}}}],
            [{"type": "tool_use", "id": "call_0", "name": "get_weather", "input": {}}],
            id="synthetic_tool_id",
        ),
        pytest.param(
            [{"text": "reasoning", "thought": True}, {"text": "answer"}],
            [
                {"type": "thinking", "thinking": "reasoning"},
                {"type": "text", "text": "answer"},
            ],
            id="thinking_then_text",
        ),
    ],
)
async def test_response_blocks(stream, parts, expected):
    assert await _response_blocks(parts, stream=stream) == expected


@pytest.mark.parametrize(
    "model, expected",
    [
        pytest.param("claude-sonnet-5", "claude-sonnet-5", id="requested"),
        pytest.param(None, "", id="backend_default"),
    ],
)
def test_response_model(model, expected):
    data = _completion([{"text": "Hello!"}])
    assert _to_anthropic(data, model=model)["model"] == expected


@pytest.mark.parametrize(
    "usage, expected",
    [
        pytest.param(None, {"input_tokens": 0, "output_tokens": 0}, id="missing"),
        pytest.param(
            {"promptTokenCount": 100, "candidatesTokenCount": 20},
            {"input_tokens": 100, "output_tokens": 20},
            id="uncached",
        ),
        pytest.param(
            {"promptTokenCount": 100, "cachedContentTokenCount": 0},
            {"input_tokens": 100, "output_tokens": 0, "cache_read_input_tokens": 0},
            id="zero_cache_reported",
        ),
        pytest.param(
            {
                "promptTokenCount": 100,
                "cachedContentTokenCount": 60,
                "candidatesTokenCount": 20,
                "thoughtsTokenCount": 30,
            },
            {"input_tokens": 40, "output_tokens": 50, "cache_read_input_tokens": 60},
            id="cached_and_thoughts",
        ),
    ],
)
def test_usage_mapping(usage, expected):
    data = _completion([{"text": "x"}], usage=usage)
    assert _to_anthropic(data)["usage"] == expected


async def test_stream_event_sequence_with_final_usage():
    events = await _collect(
        [
            _chunk(parts=[{"text": "hi"}]),
            _chunk(finish_reason="STOP", usage=USAGE_META),
        ]
    )
    assert [name for name, _ in events] == [
        "message_start",
        "content_block_start",
        "content_block_delta",
        "content_block_stop",
        "message_delta",
        "message_stop",
    ]
    assert events[-2][1]["usage"] == {
        "input_tokens": 40,
        "output_tokens": 20,
        "cache_read_input_tokens": 60,
    }


WEATHER_CALL = {"functionCall": {"name": "get_weather", "args": {}, "id": "c"}}


@pytest.mark.parametrize(
    "stream", [pytest.param(False, id="complete"), pytest.param(True, id="stream")]
)
@pytest.mark.parametrize(
    "parts, finish_reason, expected, warns",
    [
        pytest.param([{"text": "x"}], "STOP", "end_turn", False, id="stop"),
        pytest.param([{"text": "x"}], None, "end_turn", False, id="missing"),
        pytest.param([{"text": "x"}], "MAX_TOKENS", "max_tokens", False, id="max"),
        pytest.param([{"text": "x"}], "SAFETY", "refusal", False, id="safety"),
        pytest.param([WEATHER_CALL], "STOP", "tool_use", False, id="tool_call"),
        pytest.param(
            [WEATHER_CALL], "MAX_TOKENS", "max_tokens", False, id="max_over_tool"
        ),
        pytest.param(
            [], "MALFORMED_FUNCTION_CALL", "end_turn", True, id="malformed_call"
        ),
        pytest.param([], "UNEXPECTED_TOOL_CALL", "end_turn", True, id="unexpected"),
    ],
)
async def test_stop_reason_mapping(
    stream, parts, finish_reason, expected, warns, caplog
):
    with caplog.at_level("WARNING", logger="padwan_ai"):
        if stream:
            events = await _collect([_chunk(parts=parts, finish_reason=finish_reason)])
            stop_reason = events[-2][1]["delta"]["stop_reason"]
        else:
            data = _completion(parts, finish_reason=finish_reason)
            stop_reason = _to_anthropic(data)["stop_reason"]
    assert stop_reason == expected
    assert any("finishReason" in rec.message for rec in caplog.records) is warns


@pytest.mark.parametrize(
    "stream", [pytest.param(False, id="complete"), pytest.param(True, id="stream")]
)
async def test_signed_parallel_tool_round_trip(stream):
    parts = [
        {
            "functionCall": {"name": "weather", "args": {"city": "Paris"}, "id": "a"},
            "thoughtSignature": "opaque+/==",
        },
        {"functionCall": {"name": "weather", "args": {"city": "Lyon"}, "id": "b"}},
    ]
    blocks = await _response_blocks(parts, stream=stream)
    request = _to_gemini(
        _body(
            messages=[
                {"role": "assistant", "content": blocks},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": block["id"],
                            "content": "sunny",
                        }
                        for block in blocks
                    ],
                },
            ]
        )
    )
    assert request["contents"][0]["parts"] == parts
    assert request["contents"][1]["parts"] == [
        {
            "functionResponse": {
                "id": tool_id,
                "name": "weather",
                "response": {"result": "sunny"},
            }
        }
        for tool_id in ("a", "b")
    ]


@pytest.mark.parametrize(
    "messages, expected",
    [
        pytest.param(
            [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "regular",
                            "name": "weather",
                            "input": {},
                        }
                    ],
                }
            ],
            nullcontext(),
            id="plain",
        ),
        pytest.param(
            [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "gemini_signed_!",
                            "name": "weather",
                            "input": {},
                        }
                    ],
                }
            ],
            pytest.raises(ValueError, match="Invalid signed"),
            id="invalid_base64",
        ),
        pytest.param(
            [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "gemini_signed_e30",
                            "name": "weather",
                            "input": {},
                        }
                    ],
                }
            ],
            pytest.raises(ValueError, match="Invalid signed"),
            id="invalid_shape",
        ),
        pytest.param(
            [
                {
                    "role": "assistant",
                    "content": [
                        {"type": "tool_use", "id": "", "name": "weather", "input": {}}
                    ],
                }
            ],
            pytest.raises(ValueError, match="nonempty id and name"),
            id="empty_id",
        ),
        pytest.param(
            [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "missing",
                            "content": "sunny",
                        }
                    ],
                }
            ],
            pytest.raises(ValueError, match="No preceding tool_use"),
            id="orphan_tool_result",
        ),
    ],
)
def test_tool_id_validation(messages, expected):
    with expected:
        _to_gemini(_body(messages=messages))


@pytest.mark.parametrize(
    "stream", [pytest.param(False, id="complete"), pytest.param(True, id="stream")]
)
@pytest.mark.parametrize(
    "override, expected",
    [
        pytest.param(None, "gemini-2.5-flash-lite", id="body_model"),
        pytest.param("gemini-2.5-pro", "gemini-2.5-pro", id="explicit_model"),
    ],
)
async def test_converted_request_selects_endpoint(
    stream, override, expected, make_resp, make_sse_resp
):
    client = GeminiClient(api_key="test", model="gemini-2.5-flash")
    session = AsyncMock()
    client._session = session
    body = messages_to_gemini(
        _body(
            tool_choice={"type": "any"},
            tools=[
                {
                    "name": "weather",
                    "input_schema": {"type": "object", "properties": {}},
                }
            ],
        ),
        model="gemini-2.5-flash-lite",
    )
    before = dict(body)
    if stream:
        session.post.return_value = make_sse_resp([])
        _ = [chunk async for chunk in client.stream(body, model=override)]
        suffix = "streamGenerateContent"
    else:
        session.post.return_value = make_resp(200, _completion([]))
        await client.complete(body, model=override)
        suffix = "generateContent"
    args, kwargs = session.post.call_args
    assert args[0].split("?")[0].endswith(f"/models/{expected}:{suffix}")
    expected_json: dict[str, Any] = {k: v for k, v in body.items() if k != "model"}
    if stream:
        # stream() layers the request's generationConfig over the client defaults.
        expected_json["generationConfig"] = {
            "temperature": client.temperature,
            **body.get("generationConfig", {}),
        }
    assert kwargs["json"] == expected_json
    assert body == before
