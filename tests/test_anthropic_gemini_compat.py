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


def test_model_kept_when_not_overridden():
    request = _to_gemini(_body())
    assert request["model"] == "claude-sonnet-5"


def test_max_tokens_maps_to_generation_config():
    request = _to_gemini(_body(), model="gemini-2.5-flash")
    assert request["generationConfig"]["maxOutputTokens"] == 1024
    assert request["model"] == "gemini-2.5-flash"


def test_plain_text_user_message_becomes_content():
    request = _to_gemini(_body(), model="gemini-2.5-flash")
    assert request["contents"] == [{"role": "user", "parts": [{"text": "hello"}]}]


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
    ],
)
def test_system_maps_to_system_instruction(system, expected):
    request = _to_gemini(_body(system=system), model="gemini-2.5-flash")
    assert request["systemInstruction"] == {"parts": [{"text": expected}]}


def test_empty_system_omitted():
    request = _to_gemini(_body(system=""), model="gemini-2.5-flash")
    assert "systemInstruction" not in request


def test_image_block_becomes_inline_data():
    body = _body(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "describe this"},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": BASE64_PNG,
                        },
                    },
                ],
            }
        ]
    )
    request = _to_gemini(body, model="gemini-2.5-flash")
    parts = request["contents"][0]["parts"]
    assert parts == [
        {"text": "describe this"},
        {"inlineData": {"mimeType": "image/png", "data": BASE64_PNG}},
    ]


def test_assistant_tool_use_becomes_function_call():
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
                        "input": {"city": "Paris"},
                    }
                ],
            },
        ]
    )
    request = _to_gemini(body, model="gemini-2.5-flash")
    assert request["contents"][1] == {
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


def test_tool_result_becomes_function_response():
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
                        "input": {"city": "Paris"},
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "call_1",
                        "content": '{"temp": 18}',
                    }
                ],
            },
        ]
    )
    request = _to_gemini(body, model="gemini-2.5-flash")
    tool_result = request["contents"][2]
    assert tool_result["role"] == "user"
    assert tool_result["parts"][0]["functionResponse"] == {
        "id": "call_1",
        "name": "get_weather",
        "response": {"temp": 18},
    }


def test_thinking_blocks_dropped_on_replay():
    body = _body(
        messages=[
            {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "reasoning here"},
                    {"type": "text", "text": "answer"},
                ],
            },
        ]
    )
    request = _to_gemini(body, model="gemini-2.5-flash")
    assert request["contents"][0] == {
        "role": "model",
        "parts": [{"text": "answer"}],
    }


def test_tools_map_to_function_declarations():
    body = _body(
        tools=[
            {
                "name": "get_weather",
                "description": "Get the weather",
                "input_schema": {"type": "object", "properties": {}},
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
                    "parameters": {"type": "object", "properties": {}},
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


def test_sampling_params_mapped():
    body = _body(temperature=0.7, top_p=0.9, top_k=40, stop_sequences=["END"])
    request = _to_gemini(body, model="gemini-2.5-flash")
    gc = request["generationConfig"]
    assert gc["temperature"] == 0.7
    assert gc["topP"] == 0.9
    assert gc["topK"] == 40
    assert gc["stopSequences"] == ["END"]


# gemini_response_to_anthropic


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


def test_text_response():
    data = _completion([{"text": "Hello!"}])
    resp = _to_anthropic(data, model="claude-sonnet-5")
    assert resp["content"] == [{"type": "text", "text": "Hello!"}]
    assert resp["stop_reason"] == "end_turn"
    assert resp["role"] == "assistant"
    assert resp["model"] == "claude-sonnet-5"
    assert resp["usage"] == {
        "input_tokens": 100,
        "output_tokens": 20,
        "cache_read_input_tokens": 60,
    }


def test_model_defaults_to_backend():
    data = _completion([{"text": "Hello!"}])
    assert _to_anthropic(data)["model"] == ""


def test_tool_use_response():
    data = _completion(
        [
            {
                "functionCall": {
                    "name": "get_weather",
                    "args": {"city": "Paris"},
                    "id": "call_9",
                }
            }
        ]
    )
    resp = _to_anthropic(data, model="claude-sonnet-5")
    assert resp["content"] == [
        {
            "type": "tool_use",
            "id": "call_9",
            "name": "get_weather",
            "input": {"city": "Paris"},
        }
    ]
    assert resp["stop_reason"] == "tool_use"


def test_synthetic_tool_id_when_missing():
    data = _completion([{"functionCall": {"name": "get_weather", "args": {}}}])
    resp = _to_anthropic(data, model="claude-sonnet-5")
    assert resp["content"][0]["id"] == "call_0"


def test_thinking_part_becomes_thinking_block():
    data = _completion([{"text": "reasoning", "thought": True}, {"text": "answer"}])
    resp = _to_anthropic(data, model="claude-sonnet-5")
    assert resp["content"] == [
        {"type": "thinking", "thinking": "reasoning"},
        {"type": "text", "text": "answer"},
    ]


@pytest.mark.parametrize(
    "finish_reason, expected",
    [
        pytest.param("STOP", "end_turn", id="stop"),
        pytest.param("MAX_TOKENS", "max_tokens", id="max_tokens"),
        pytest.param("SAFETY", "refusal", id="safety"),
    ],
)
def test_finish_reason_mapping(finish_reason, expected):
    data = _completion([{"text": "x"}], finish_reason=finish_reason)
    assert _to_anthropic(data, model="claude-sonnet-5")["stop_reason"] == expected


# gemini_stream_to_anthropic


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


def _event_names(events):
    return [name for name, _ in events]


async def test_stream_text():
    events = await _collect([_chunk(parts=[{"text": "Hello"}])])
    assert _event_names(events) == [
        "message_start",
        "content_block_start",
        "content_block_delta",
        "content_block_stop",
        "message_delta",
        "message_stop",
    ]
    assert events[2][1]["delta"] == {"type": "text_delta", "text": "Hello"}


async def test_stream_tool_call_whole_args():
    events = await _collect(
        [
            _chunk(
                parts=[
                    {
                        "functionCall": {
                            "name": "get_weather",
                            "args": {"city": "Paris"},
                            "id": "call_1",
                        }
                    }
                ]
            )
        ]
    )
    # Locate the input_json_delta event.
    deltas = [
        payload["delta"]
        for _, payload in events
        if payload.get("type") == "content_block_delta"
    ]
    assert deltas[-1]["type"] == "input_json_delta"
    assert json.loads(deltas[-1]["partial_json"]) == {"city": "Paris"}
    start = events[1][1]
    assert start["content_block"]["type"] == "tool_use"
    assert start["content_block"]["name"] == "get_weather"
    assert events[-2][1]["delta"]["stop_reason"] == "tool_use"


async def test_stream_thinking_then_text():
    events = await _collect(
        [_chunk(parts=[{"text": "thought", "thought": True}, {"text": "answer"}])]
    )
    block_starts = [
        payload["content_block"]["type"]
        for _, payload in events
        if payload.get("type") == "content_block_start"
    ]
    assert block_starts == ["thinking", "text"]


async def test_stream_usage_on_final_chunk():
    events = await _collect(
        [
            _chunk(parts=[{"text": "hi"}]),
            _chunk(finish_reason="STOP", usage=USAGE_META),
        ]
    )
    assert events[-2][1]["usage"] == {
        "input_tokens": 100,
        "output_tokens": 20,
        "cache_read_input_tokens": 60,
    }


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
    if stream:
        events = await _collect([_chunk(parts=parts)])
        blocks = []
        for name, event in events:
            if name == "content_block_start":
                blocks.append(event["content_block"].copy())
            elif name == "content_block_delta":
                blocks[-1]["input"] = json.loads(event["delta"]["partial_json"])
    else:
        blocks = _to_anthropic(_completion(parts))["content"]
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
    "tool_id, expected",
    [
        pytest.param("regular", nullcontext(), id="plain"),
        pytest.param(
            "gemini_signed_!",
            pytest.raises(ValueError, match="Invalid signed"),
            id="invalid_base64",
        ),
        pytest.param(
            "gemini_signed_e30",
            pytest.raises(ValueError, match="Invalid signed"),
            id="invalid_shape",
        ),
    ],
)
def test_tool_id_validation(tool_id, expected):
    with expected:
        _to_gemini(
            _body(
                messages=[
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": tool_id,
                                "name": "weather",
                                "input": {},
                            }
                        ],
                    }
                ]
            )
        )


def test_orphan_tool_result_rejected():
    with pytest.raises(ValueError, match="No preceding tool_use"):
        _to_gemini(
            _body(
                messages=[
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
                ]
            )
        )


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
    assert args[0].endswith(f"/models/{expected}:{suffix}")
    assert kwargs["json"] == {
        key: value for key, value in body.items() if key != "model"
    }
    assert body == before
