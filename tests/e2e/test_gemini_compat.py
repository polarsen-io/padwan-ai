from typing import Any, cast

import pytest

from padwan_ai import GeminiClient
from padwan_ai.anthropic.gemini_compat import (
    gemini_response_to_anthropic,
    gemini_stream_to_anthropic,
    messages_to_gemini,
)
from padwan_ai.anthropic.models import AnthropicCompatBody

from .conftest import skip_no_gemini

pytestmark = [pytest.mark.e2e, skip_no_gemini]

GEMINI_MODEL = "gemini-3.5-flash-lite"  # free tier: 3.8-flash allows 20 requests a day
CLAUDE_MODEL = "claude-sonnet-5"  # what the Anthropic-side caller asked for
WEATHER_TOOL = {
    "name": "get_weather",
    "description": "Get the current weather for a given city.",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "The city name"}},
        "required": ["city"],
    },
}


def _body(messages: list[Any], **extra: Any) -> AnthropicCompatBody:
    body = {"model": CLAUDE_MODEL, "max_tokens": 256, "messages": messages, **extra}
    return cast(AnthropicCompatBody, body)


async def _complete(client: GeminiClient, body: AnthropicCompatBody) -> dict[str, Any]:
    data, _ = await client.complete(messages_to_gemini(body, model=GEMINI_MODEL))
    response = gemini_response_to_anthropic(data, model=body["model"])
    return cast("dict[str, Any]", response)


@pytest.mark.parametrize(
    "max_tokens, expected_stop",
    [
        pytest.param(256, "end_turn", id="text"),
        pytest.param(1, "max_tokens", id="max-tokens"),
    ],
)
async def test_complete(max_tokens: int, expected_stop: str) -> None:
    body = _body(
        [{"role": "user", "content": "Reply with only the word 'hello'."}],
        max_tokens=max_tokens,
    )
    async with GeminiClient() as client:
        response = await _complete(client, body)

    assert response["model"] == CLAUDE_MODEL
    assert response["stop_reason"] == expected_stop
    assert response["usage"]["input_tokens"] > 0
    if expected_stop == "end_turn":
        assert response["content"][0]["type"] == "text"
        assert "hello" in response["content"][0]["text"].lower()


async def test_stream_events() -> None:
    body = _body([{"role": "user", "content": "Reply with only the word 'hello'."}])
    request = messages_to_gemini(body, model=GEMINI_MODEL)
    async with GeminiClient() as client:
        events = [
            event
            async for event in gemini_stream_to_anthropic(
                client.stream(request), model=CLAUDE_MODEL
            )
        ]

    names = [name for name, _ in events]
    assert names[0] == "message_start"
    assert names[-1] == "message_stop"
    assert names.index("content_block_start") < names.index("message_delta")
    text = "".join(
        payload["delta"]["text"]
        for name, payload in events
        if name == "content_block_delta" and payload["delta"]["type"] == "text_delta"
    )
    assert "hello" in text.lower()
    message_delta = next(payload for name, payload in events if name == "message_delta")
    assert message_delta["delta"]["stop_reason"] == "end_turn"
    assert message_delta["usage"]["output_tokens"] > 0


async def test_tool_use_roundtrip() -> None:
    """Replaying Gemini's signed function-call IDs only works live, mocks can't tell."""
    messages: list[Any] = [{"role": "user", "content": "What is the weather in Paris?"}]
    async with GeminiClient() as client:
        first = await _complete(client, _body(messages, tools=[WEATHER_TOOL]))
        assert first["stop_reason"] == "tool_use"
        tool_use = next(b for b in first["content"] if b["type"] == "tool_use")
        assert tool_use["name"] == "get_weather"
        assert "paris" in tool_use["input"]["city"].lower()

        messages += [
            {"role": "assistant", "content": first["content"]},  # IDs kept as returned
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use["id"],
                        "content": "18°C and sunny",
                    }
                ],
            },
        ]
        final = await _complete(client, _body(messages, tools=[WEATHER_TOOL]))

    assert final["stop_reason"] == "end_turn"
    text = "".join(b["text"] for b in final["content"] if b["type"] == "text")
    assert "18" in text
