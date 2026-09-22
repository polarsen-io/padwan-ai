# Anthropic Client

The Anthropic client provides access to Claude models through the native
[Messages API](https://platform.claude.com/docs/en/api/messages). It is a
standalone client (not OpenAI-compatible).

## Configuration

```python
from padwan_ai.anthropic import AnthropicClient

client = AnthropicClient(
    api_key="...",  # or set ANTHROPIC_API_KEY env var
    model="claude-opus-4-8",  # default model
    max_tokens=4096,  # required by the Messages API, per-response cap
)
```

!!! note "Sampling parameters"
    Current Claude models reject non-default sampling parameters, so the
    inherited `temperature` field is never sent — steer behavior via the
    prompt instead.

## Usage

### Basic Chat

```python
from padwan_ai.conversation import Message

async with AnthropicClient() as client:
    response, usage = await client.complete_chat(
        [Message(role="user", content="Hello!")]
    )
    print(response["content"])
```

### Streaming

```python
from padwan_ai.conversation import Message

async with AnthropicClient() as client:
    stream = client.stream_chat([Message(role="user", content="Tell me a story")])
    async for chunk in stream:
        print(chunk, end="")
```

### With System Prompt

System messages are translated to the Messages API's top-level `system` field.

```python
from padwan_ai import ConversationState

state = ConversationState(system="You are a helpful assistant.")
state.add_user_message("Hello!")

async with AnthropicClient() as client:
    response, usage = await client.complete_chat(state.messages)
    state.add_assistant_message(response["content"])
    state.accumulate_usage(usage)
```

### Tool Calling

`tool_use` blocks map to the shared `ToolCall` shape; send results back as
`ToolResultMessage`s.

```python
from padwan_ai.models import ToolDefinition

WEATHER_TOOL: ToolDefinition = {
    "name": "get_weather",
    "description": "Get the current weather for a given city.",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
}

async with AnthropicClient() as client:
    response, _ = await client.complete_chat(
        [{"role": "user", "content": "Weather in Paris?"}],
        tools=[WEATHER_TOOL],
    )
    call = response["tool_calls"][0]

    response2, _ = await client.complete_chat(
        [
            {"role": "user", "content": "Weather in Paris?"},
            {"role": "assistant", "content": response["content"], "tool_calls": [call]},
            {
                "role": "tool",
                "tool_call_id": call["id"],
                "name": "get_weather",
                "content": "18°C",
            },
        ],
        tools=[WEATHER_TOOL],
    )
```

### Thinking

Claude models think adaptively by default. Summarized thinking (when exposed
by the model) is forwarded to the `on_thought` callback and never leaks into
the answer text.

```python
async with AnthropicClient(
    model="claude-opus-4-8",
    on_thought=lambda t: print(f"[thinking] {t}"),
) as client:
    response, _ = await client.complete_chat(
        [{"role": "user", "content": "What is 7 * 8?"}]
    )
```

## Method Outputs

```python
response, usage = await client.complete_chat(messages)
# usage["cached"] carries cache_read_input_tokens when present

stream = client.stream_chat(messages)
async for chunk in stream:
    ...
usage = stream.usage
tool_calls = stream.tool_calls
```

## Messages compatibility over Gemini

Like `anthropic.compat.messages_to_openai` and `anthropic.events`, the
`anthropic.gemini_compat` module translates Messages requests and responses
without running an HTTP server.

```python
from padwan_ai.anthropic.gemini_compat import (
    gemini_response_to_anthropic,
    gemini_stream_to_anthropic,
    messages_to_gemini,
)
from padwan_ai.anthropic.models import AnthropicCompatBody
from padwan_ai.gemini import GeminiClient

body: AnthropicCompatBody = {
    "model": "claude-sonnet-5",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello!"}],
}
request = messages_to_gemini(body, model="gemini-2.5-flash")
async with GeminiClient() as client:
    data, usage = await client.complete(request)
    response = gemini_response_to_anthropic(data, model=body["model"])

    async for event_name, payload in gemini_stream_to_anthropic(
        client.stream(request), model=body["model"]
    ):
        ...  # The server serializes these pairs as SSE frames.
```

The converted `model` selects the client endpoint and is removed from the
HTTP body. An explicit `complete(..., model=...)` or `stream(..., model=...)`
argument takes precedence.

Keep returned tool IDs unchanged when replaying assistant calls and user
results: signed Gemini function calls carry their signatures in those opaque
IDs. Parallel results stay together in one user turn; unmatched results raise
`ValueError`. Anthropic thinking blocks and thinking configuration are not
replayed. Signatures attached to non-function parts are not preserved. Remote
image URLs, server tools, and non-text tool-result content are not translated.
