<p align="center">
  <img src="docs/static/logo-hood.png" alt="Padwan AI" width="120">
</p>

<h1 align="center">Padwan AI</h1>

<p align="center">
  Lightweight async client for OpenAI, Gemini, Mistral, Grok, Anthropic, and any OpenAI-compatible API.<br>
  One runtime dependency (<a href="https://github.com/jawah/niquests">niquests</a>), TypedDict everywhere, HTTP/2 and HTTP/3 out of the box.
</p>

<p align="center">
  <a href="https://polarsen-io.github.io/padwan-ai">Documentation</a> ·
  <a href="https://pypi.org/project/padwan-ai/">PyPI</a> ·
  <a href="CHANGELOG.md">Changelog</a>
</p>

## Install

```bash
pip install padwan-ai
```

Extras: `[realtime]` for voice sessions, `[otel]` for OpenTelemetry, `[langfuse]` for the Langfuse adapter.

## Quickstart

```python
from padwan_ai import LLMClient

async with LLMClient(model="gpt-5.5") as client:
    response, usage = await client.complete_chat(
        [{"role": "user", "content": "Hello!"}]
    )
    print(response["content"])
```

The provider is picked from the model name; only the matching `*_API_KEY` env var is needed.

### Streaming

```python
from padwan_ai import ConversationState, LLMClient

state = ConversationState(system="You are a concise assistant.")
state.add_user_message("What's Python?")

async with LLMClient(model="gemini-3.5-flash") as client:
    chunks: list[str] = []
    async for text in client.stream_chat(state.messages):
        print(text, end="", flush=True)
        chunks.append(text)
    state.add_assistant_message("".join(chunks))
```

### Agent with tools

`AgentSession` runs the tool loop: call the model, dispatch tool calls, feed results back, repeat until a final answer. Tools come from typed Python functions or from MCP servers.

```python
from padwan_ai import AgentSession, LLMClient, McpStdio
from padwan_ai.tools import tool


@tool
async def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


async with AgentSession(
    client=LLMClient(model="claude-sonnet-5"),
    mcp_tools=[add, McpStdio(command="uvx", args=["my-mcp-server"])],
    system="Use tools when helpful.",
) as session:
    print(await session.send("What is 2 + 3, and what's the weather in Paris?"))
```

Typed final answers (`AgentOutput`), approval hooks, parallel tool execution and snapshot persistence are covered in the [agents guide](docs/agents.md).

### One-shot from the shell

```bash
uvx padwan-ai "Hello!" -m gpt-5.4-mini
```

For an interactive chat TUI use [`padwan-cli`](https://github.com/polarsen-io/padwan-cli).

## Providers

| Provider | Chat + streaming | Batch | Realtime voice |
|----------|:-:|:-:|:-:|
| OpenAI | ✅ | ✅ | ✅ |
| Gemini | ✅ | ✅ | ✅ |
| Anthropic | ✅ | ❌ | ❌ |
| Mistral | ✅ | ❌ | ❌ |
| Grok | ✅ | ✅ | ✅ |
| OpenAI-compatible (`base_url=`) | ✅ | depends on the server | |

Thinking tokens stream separately through an `on_thought` callback on every client that exposes them. Per-provider details, multimodal input (images, audio, files) and embeddings: [docs/clients](docs/clients/), [docs/multimodal.md](docs/multimodal.md).

**TypeSafe (JEV)** structured evaluations (Noul, Choice, Score questions) use the standalone [`TypeSafeClient`](docs/clients/typesafe.md).

## More

- **MCP**: streamable-HTTP and stdio transports, usable standalone or inside an agent. [docs/mcp.md](docs/mcp.md)
- **Realtime voice**: `RealtimeClient` speech-to-speech over WebSocket for OpenAI, Gemini Live and Grok Voice. [docs/clients/openai.md](docs/clients/openai.md)
- **Observability**: opt-in OpenTelemetry GenAI spans and metrics with `otel.instrument()`, or a one-call Langfuse adapter. Ships a Grafana dashboard. [docs/observability.md](docs/observability.md)
- **Gateway mode**: route every model through one OpenAI-compatible endpoint with `PADWAN_BASE_URL` and `PADWAN_API_KEY`. [docs/clients/openai-compatible.md](docs/clients/openai-compatible.md)
- **Testing agents**: `padwan_ai.testing.ScriptedClient` replays scripted responses, no API key needed. [docs/agents.md](docs/agents.md)

## Development

```bash
uv sync --all-extras --all-groups
just ci          # ruff + pyright + pytest
just e2e         # live provider tests, keys from .env (see env.template)
just docs        # serve the docs site locally
```
