## 0.13.0 (2026-09-24)

Gemini text-to-speech, MCP progress and cancellation that actually reach the server, and docs re-checked against the code.

### Breaking

- **`OpenAIClient` no longer sends `OPENAI_API_KEY` to a non-OpenAI `base_url`.** Without an explicit `api_key`, any host other than `api.openai.com` (Scaleway, a local vLLM, a proxy) now falls back to `PADWAN_API_KEY`, then `"no-key-required"`. Proxies that relied on the implicit `OPENAI_API_KEY` must pass `api_key=`. Also applies to `OpenAIRealtimeClient`. (#98)

### Features

- **Gemini text-to-speech**: `GeminiClient.generate_speech()` for the Gemini 3.8 TTS models (`gemini-3.8-flash-tts`, `gemini-3.8-flash-lite-tts`) and the 2.5/3.1 TTS models. Single voice or `{speaker: voice}` multi-speaker, optional `language_code`, script lines tagged with `speechMetadata`. Returns `(GeminiSpeech(audio, mime_type), usage)`. (#95)

```python
async with GeminiClient(model="gemini-3.8-flash-tts") as client:
    speech, usage = await client.generate_speech("Hello!", voice="Puck")
```

- **vLLM reasoning deltas**: the OpenAI stream parser also reads vLLM's `reasoning` field alongside `reasoning_content`. (#94)

### Fixes

- **MCP progress**: `tools/call` sends `_meta.progressToken` when `on_progress` is set, so spec-compliant servers now report progress. (#98)
- **MCP cancellation**: cancelling the task awaiting a tool call sends `notifications/cancelled` for that request (best-effort, 1s cap), then re-raises. (#98)
- **MCP listener**: warns when the GET listener gives up after 5 consecutive reconnect failures instead of stopping silently. (#98)
- **Async `on_mcp_connect`** callbacks are now awaited. (#98)
- **Grok batch** forwards the full request body (`temperature`, `tools`, ...) instead of only `messages`. (#98)
- **urllib3-future 2.25.900** for concurrent WebSocket reads/writes; Gemini `RetryInfo` delays restored with a `Retry-After` fallback; SSE streams propagate task cancellation; non-streaming chat accepts provider parameters. (#92)

### Docs

- Every page re-verified against the code: fixed wrong claims (inheritance of Mistral/Grok, `otel.instrument()` idempotency, audio formats, agent dispatch order and denial message, `JsonStore` example), documented MCP transport parameters, name collisions and session recovery. (#98)
- Provider logos in the site nav. (#98)

### Dev

- E2E runs on the `e2e` label or manual dispatch, one parallel job per test file. (#96)
- Observability recipes moved into a `just` module. (#97)
- Weekly LLM SDK refresh. (#90)

## 0.12.1 (2026-09-20)

### Fixes

- **PyPI metadata**: `description`, `readme`, `license = "MIT"` (with `license-files`) and `[project.urls]` (Homepage, Source, Changelog) were all absent, so the PyPI page showed no summary, README, links or license. The MIT trove classifier is dropped — PEP 639 rejects it alongside a license expression. (#88)
- **README links absolutized** (logo image, changelog) so they resolve in the PyPI-rendered description. (#88)
- **`py.typed` marker shipped** (PEP 561). The package declared `Typing :: Typed` but had no marker file, so downstream type checkers ignored its inline annotations. (#88)

## 0.12.0 (2026-09-20)

Embeddings for every provider that offers them, plus a Voyage AI client.

### Breaking

- **`MistralClient.fetch_embeddings` no longer defaults to `mistral-embed`.** Pass `model=` on the client or on the call. (#85)

### Features

- **Embeddings on every provider.** `_OpenAIBase.fetch_embeddings(input, model=None, *, dimensions=None, extra_params=None)` serves OpenAI, Mistral, Grok, Voyage and custom `base_url` endpoints, and `GeminiClient` gets a native `batchEmbedContents` implementation. Both return the raw provider payload. (#85)
- **Voyage AI client** (the provider Anthropic recommends for embeddings), with `VoyageModel` and `VOYAGE_MODELS`. (#85)
- **`padwan_ai.vectors(resp, provider)`** pulls the vectors out of either payload shape in input order: Gemini is ordered by contract, OpenAI-shaped payloads are sorted by `index`. (#85)
- **`OpenAIEmbeddingModel` and `GeminiEmbeddingModel` literals**, and `LLMClient` routes `text-embedding-*` and `voyage-*` model ids. (#85)

```python
async with OpenAIClient(model="text-embedding-3-small") as client:
    vecs = vectors(await client.fetch_embeddings(["a", "b"], dimensions=256))
```

### Observability

- **OpenTelemetry wraps `fetch_embeddings`** on the OpenAI base and on Gemini, emitting the semconv recommended `gen_ai.embeddings.dimension.count` (derived from the returned vectors), `gen_ai.request.encoding_formats`, `gen_ai.response.model` and `gen_ai.usage.input_tokens`, the last also recorded on `gen_ai.client.token.usage`. (#85)

### Docs

- **TypeSafe (JEV) is labelled experimental** in the README, the docs landing page, the site nav and an admonition on its page: the interface may change between minor releases without a deprecation cycle. (#84)
- Provider matrices now distinguish "not implemented yet" (❌) from "the provider has no such API" (➖). (#85)

### Dev

- The weekly drift report tracks OpenAI and Gemini embedding models. (#85)
- **Import benchmarks no longer flake on runner speed.** Times are normalised by interpreter startup and rescaled to a reference runner, and the perf job syncs only the otel extra instead of every group, which removed 3m33s of source builds on the 3.15 prerelease. Every Python version reports in a single PR comment. (#85, #86)

**Full Changelog**: https://github.com/polarsen-io/padwan-ai/compare/0.11.1...0.12.0

## 0.11.1 (2026-09-20)

Docs and packaging release.

### Changes

- **README rewritten as a short landing page**: install, three examples (chat, streaming, agent with a typed tool and an MCP server), provider table, one link per feature area, badges for PyPI version, Python versions and CI. Everything removed already lives in the docs site. (#82)
- **Trove classifiers** in package metadata (MIT, Python 3.13 to 3.15, typed), so PyPI and the Python-versions badge report supported versions. (#82)
- **Release workflow can be re-dispatched** for an existing tag (`gh workflow run release.yml -f version=X.Y.Z`): tagging is skipped when the tag exists and the GitHub Release notes are reused, so a failed PyPI publish no longer requires re-cutting the release. (#81)

**Full Changelog**: https://github.com/polarsen-io/padwan-ai/compare/0.11.0...0.11.1

## 0.11.0 (2026-09-19)

Rename release: the project is now **padwan-ai**. Plus a native TypeSafe (JEV) client.

### Breaking

- **Package renamed `padwan-llm` -> `padwan-ai`.** Install `padwan-ai` and replace `import padwan_llm` with `import padwan_ai`; the console script is now `padwan-ai`. Nothing else in the API changed. The final `padwan-llm` release (0.11.0) only depends on `padwan-ai` and raises an `ImportError` pointing at the new name, so `pip uninstall padwan-llm` after upgrading. (#79)
- **Telemetry names follow the rename.** Logger and OpenTelemetry instrumentation scope are `padwan_ai`, span attributes are `padwan_ai.response.tool_names`, `padwan_ai.thinking.duration` and `padwan_ai.response.first_chunk_time`, and the MCP `clientInfo.name` default is `padwan-ai`. Update dashboards and log filters keyed on the old names. Metric names are unchanged (`gen_ai.*`). (#79)
- Repository and docs moved to https://github.com/polarsen-io/padwan-ai and https://polarsen-io.github.io/padwan-ai. The Grafana dashboard uid is `padwan-ai-genai`.

### Features

- **TypeSafe (JEV) client.** `TypeSafeClient.system_one()` evaluates text or structured state against named Noul, Choice and Score questions through the System One API, with typed request and response dictionaries, niquests retries on connection errors, timeouts, 408/429 and 5xx, and `TooManyRequestsError` / `LLMError(provider="typesafe")` on failure. `TypeSafeModel` and `TYPESAFE_MODELS` track the `jev-latest` and `jev-preview` aliases; the API key comes from `TYPESAFE_API_KEY`. Payload validation is left to the API. (#78, #79)

### Dev

- The weekly model-drift workflow also tracks TypeSafe models. (#78, #79)
- Live TypeSafe e2e tests and a TypeSafe docs page. (#78, #79)

**Full Changelog**: https://github.com/polarsen-io/padwan-ai/compare/0.10.1...0.11.0

## 0.10.1 (2026-09-16)

### Fix

- **otel**: instrument raw calls on all OpenAI-compatible clients (#76)

`otel.instrument()` patched `complete`/`stream` on `OpenAIClient`, but both are
defined on `_OpenAIBase` and `OpenAIClient` does not override them — so the
patch never reached sibling subclasses such as `MistralClient`. Any client
built for an OpenAI-compatible endpoint that called the raw `complete()` /
`stream()` path emitted no spans and no metrics at all. Patching `_OpenAIBase`
covers every such client; `complete_chat`/`stream_chat` were unaffected.

## 0.10.0 (2026-09-14)

Agent release: typed answers, tools built from typed functions with a pluggable validator, and a scripted client for testing agents. Plus Langfuse time to first token and OpenTelemetry fixes.

### Features

- **Typed final answers.** `AgentSession(output=AgentOutput(Verdict))` adds a `submit` tool whose parameters are the answer's JSON Schema; `run()` drives the loop until a call validates and returns the instance. The answer class is a `msgspec.Struct` or a `pydantic.BaseModel`, validated by its own library. An invalid call (or arguments that are not JSON) goes back to the model up to `max_repairs` times, then `OutputError`; a text answer or the round limit raise `OutputError` too. `run()` is typed: `AgentSession[Verdict]` returns a `Verdict`. (#73)
- **Tools from typed functions.** `padwan_ai.tools.tool(fn)` builds an `McpTool` from a typed async function: the signature is the schema, the docstring the description, and the arguments are validated and coerced before the function runs. `validator=` picks msgspec or pydantic, or any `ToolValidator`; with none given, the annotations decide. Neither library is a dependency. (#67)
- **Scripted client for tests.** `padwan_ai.testing.ScriptedClient` replays a script of `Step`s (text and/or tool calls) in place of a provider, records every round's request, and raises when the script runs out. (#59)
- **Langfuse time to first token.** Streamed chat spans record the first chunk time, mapped to Langfuse's `completion_start_time`. `langfuse.instrument()` also accepts `span_exporter` and `httpx_client`, so a test can capture every attribute without a socket. (#69, #70)

### Fixes

- **Raw OpenAI `complete()` / `stream()` calls are traced** when no chat span is open, with usage, finish reasons, tool names and time to first chunk. (#55)
- **Caller context restored between stream chunks**, so unrelated work no longer inherits the chat span and cross-task iteration no longer raises. (#58)
- **Audio formats inferred from file extensions**, so `.m4a` / `.aac` files are accepted regardless of the host's MIME mappings. (#57)
- **`padwan_ai.langfuse` imports on Python 3.13**; `httpx` stays a type-only import and a missing optional dependency is still reported as Langfuse. (#71, #72)

### Dev

- Unparsable tool-call arguments are returned to the model as an error for every tool instead of running the handler on `{}`. (#73)
- Weekly LLM SDK refreshes; the perf workflow skips benchmark comments on fork PRs. (#54, #56, #65, #68)

**Full Changelog**: https://github.com/polarsen-io/padwan-ai/compare/0.9.4...0.10.0

## 0.9.4 (2026-08-25)

### Changes

- **Anthropic SDK 1.0 support.** Requires `anthropic>=1.0.0`, aligns the native request type with the new SDK, and preserves legacy sampling fields in the Anthropic-to-OpenAI compatibility layer. (#49)
- **Mistral-hosted GLM 5.2 routing.** Adds both live model IDs, `glm-5-2` and `zai-glm-5-2`, and routes both prefixes through the Mistral client. (#49)
- **Provider SDK refresh.** Updates Google GenAI to 2.19.0 and OpenAI to 3.3.1, with regenerated OpenAI and Mistral API types. (#49)

## 0.9.3 (2026-08-25)

### Changes

- **urllib3-future floor raised to 2.24.904.** Carries the upstream fix for the HTTP/2 stream reset raising on already-closed SSE streams (jawah/urllib3.future#406), so streams no longer rely solely on 0.9.2's best-effort cleanup for that case. (#51)

## 0.9.2 (2026-08-24)

- **SSE cleanup is now best-effort across all streaming clients (OpenAI-compatible, Anthropic, Gemini).** 0.9.1's stream cleanup was unguarded: over HTTP/2 backends, closing a stream the server had already half-closed raised an exception (`jh2.StreamClosedError`, see jawah/urllib3.future#406) that corrupted every successful streamed response, and on HTTP/1.1 the connection lease could stay held until garbage collection, starving the pool after ~10 back-to-back streams. Each cleanup step (extension close, raw response teardown, pool release) is now guarded and failures are logged at debug level. (#48)

## 0.9.1 (2026-08-23)

Patch release: streaming no longer leaks pooled connections when a stream ends on the `[DONE]` sentinel or is abandoned mid-read.

### Fixes

- **Half-read SSE streams starved the connection pool** — a stream that ended on the `[DONE]` sentinel (or was abandoned by its consumer, e.g. a client abort) left its response half-read, keeping the pooled connection leased until garbage collection; a sequence of streams on one client exhausted the pool and the next `stream()` call hung forever. The duplicated per-provider SSE loops are now a single `LLMClientBase._iter_sse` helper that closes the SSE extension in a `finally`, wrapped in `contextlib.aclosing` so an abandoned stream releases its connection deterministically (#46).

**Full Changelog**: https://github.com/polarsen-io/padwan-ai/compare/0.9.0...0.9.1

## 0.9.0 (2026-08-23)

Observability release: opt-in OpenTelemetry GenAI instrumentation with a Langfuse adapter, plus an Anthropic Messages API compat layer over OpenAI backends and audio input content parts across providers.

### Features

- **OpenTelemetry GenAI instrumentation** — opt-in `padwan_ai.otel.instrument()` wraps every provider client following the GenAI semantic conventions: chat completions and streams, batch operations, embeddings, realtime sessions, agent turns and tool execution, and MCP tool calls. Emits spans plus the `gen_ai.client.operation.duration` / `gen_ai.client.token.usage` histograms, capturing reasoning tokens, thinking time, tool and conversation attributes. Content capture (prompts, responses, tool arguments/results) is off by default (`capture_content=True` to opt in). Runtime dependency is `opentelemetry-api` only, behind the `otel` extra; patching is transactional with rollback and `uninstrument()` restores the original methods (#42).
- **Langfuse adapter** — `padwan_ai.langfuse.instrument()` configures Padwan instrumentation and the Langfuse exporter together, mapping spans to Langfuse observation types (generation, embedding, agent, tool) with input/output, session-id, and cost attributes; respects `mask_otel_spans` redaction before deriving inputs/outputs. Behind the `langfuse` extra (#42).
- **Anthropic Messages API compat layer** — `padwan_ai.anthropic.compat.messages_to_openai` translates Messages API requests (system blocks, tool use, tool choice, images) to OpenAI chat-completion requests, and `padwan_ai.anthropic.events` converts responses, SSE streams, and errors back to Anthropic shapes — the building blocks for serving the Messages API over any OpenAI-compatible backend (#42).
- **Audio input content parts** — `ContentAudioPart` (OpenAI `input_audio` shape) with an `audio_part` builder; `content_parts` routes `audio/*` files automatically. OpenAI and Grok receive parts verbatim, Gemini converts to `inlineData`, Mistral rewrites to its base64 chunk. `supports_audio(model, fmt=None)` is format-aware per provider, and audio-capable providers expose `AUDIO_FORMATS` (#43).

### Performance

- Provider modules load lazily on Python 3.15 (`__lazy_modules__`), cutting `import padwan_ai` time; a new CI workflow benchmarks import times and fails on regressions (#42).

### Dev

- Local observability stack: a single docker-compose bundling Langfuse and the Grafana OTel-LGTM all-in-one, with a pre-provisioned GenAI dashboard and a `docs/observability.md` guide (#42).

**Full Changelog**: https://github.com/polarsen-io/padwan-ai/compare/0.8.0...0.9.0

## 0.8.0 (2026-08-19)

Two big additions to the unified client — a native Anthropic chat provider and multi-provider realtime voice — alongside multimodal content building blocks, runtime model-deprecation warnings, typed response decoding, and Python 3.15 support.

### Features

- **Python 3.15 support** — CI now tests 3.13 through 3.15. Grok SDK conformance tests are skipped on 3.15 until grpcio ships 3.15 wheels; the Grok client itself is unaffected (#40).
- **Anthropic client** — native `AnthropicClient` over the Messages API: `complete_chat`/`stream_chat`, tool use, SSE streaming, thinking tokens forwarded to `on_thought`, usage mapping with cache-read tokens. The `LLMClient` factory dispatches `claude-*` models; authenticates via `ANTHROPIC_API_KEY`. The weekly drift check now tracks the Anthropic model catalog (#28, #29).
- **Realtime voice clients** — `RealtimeClient` factory (mirroring `LLMClient`) dispatching by model prefix to `OpenAIRealtimeClient` (Realtime API), `GeminiRealtimeClient` (Live API), and `GrokRealtimeClient` (Voice Agent). A single `async with` opens the session, performs the handshake, and yields the connection; session config (instructions, voice, turn detection, ...) lives on the client constructor, with `NO_TURN_DETECTION` for manual push-to-talk. E2e speech roundtrips cover all three providers (#24, #35).
- **Multimodal content parts** — typed text/image/file parts in the OpenAI content-part shape, with `image_part`/`text_part`/`text_file_part` helpers and a `content_parts` builder that infers part types; `supports_vision(model)` best-effort image-input capability check (#24).
- **Model deprecation warnings** — constructing a client with a provider-retired model emits a one-time `ModelDeprecationWarning` (a `FutureWarning`, suppressible by category for deliberate pins). Deprecation maps are regenerated weekly by the drift run — no runtime network call (#23).
- **Typed response decoding** — `_check_resp(decoder=...)` deserializes provider responses through a validating decoder (e.g. msgspec) instead of untyped `.json()`; clients forward `json_encoder` to their `AsyncSession` for typed request payloads (niquests >= 3.21) (#33).
- **Gateway auth** — an explicit `base_url` with no explicit `api_key` authenticates with `PADWAN_API_KEY`, so a provider secret is never sent to a custom endpoint (#24).

### New model IDs (weekly drift runs)

- OpenAI: `gpt-5.5`
- Gemini: `gemini-3.5-flash-lite`, `gemini-3.6-flash`, `gemini-3.7-flash`, `gemini-omni-flash-preview`, `gemini-2.5-flash-native-audio-latest`
- Anthropic: `claude-opus-5`
- Mistral: `mistral-ocr-3`/`-3-0`/`-4`/`-4-0`/`-4-1`, `labs-leanstral`, `mistral-code-agent-latest`, `mistral-code-fim-latest`, `mistral-medium-3-5-0`
- Grok: `grok-4.6`, `grok-3-mini-fast-high`, `grok-3-mini-high`

### Fixes

- **Drift**: source the OpenAI spec from the official `openai/openai-openapi` repo after openai-python removed its spec pointer, unbreaking weekly type regeneration (#34).
- **Realtime**: poll websocket reads so control events (e.g. push-to-talk commits) are not blocked behind a parked read (#24).

### Chore

- Require `mcp>=2.0.0`; migrate tests to `mcp.server.mcpserver.MCPServer` (#32).
- SDK floors bumped by the weekly refreshes: openai 3.x, google-genai 2.18, ruff 0.16, pyright 1.1.411.

**Full Changelog**: https://github.com/polarsen-io/padwan-ai/compare/0.7.1...0.8.0

## 0.7.1 (2026-06-01)

Maintenance release: a Mistral model-ID correction, regenerated provider types, and a batch of improvements to the weekly model-drift automation.

### Fixes

- **Mistral**: correct the Mistral Medium 3.5 model ID from `mistral-medium-3.5` to `mistral-medium-3-5`, the form Mistral's docs and API use (#15).
- Regenerate OpenAI and Mistral OpenAPI TypedDicts against the latest SDKs (#15).

### Drift automation (tooling)

- Surface **tracked-but-deprecated** models: the drift report now reads each provider's `deprecation` field and warns before a model's retirement date, instead of only reacting once it disappears from the API (#17).
- Sign the weekly automation bot's commits with an SSH signing key so they show as **Verified** (#16).
- Emit stdlib TypedDicts via `--no-use-closed-typed-dict` during type regeneration (#14).
- Fetch the automation branch before pushing to avoid stale-ref push failures (#12).

**Full Changelog**: https://github.com/polarsen-io/padwan-ai/compare/0.7.0...0.7.1

## 0.7.0 (2026-05-15)

### Features

- **Model drift workflow** — weekly Monday cron (`model-drift.yml`) that bumps the `llms` dependency group, regenerates OpenAI/Mistral OpenAPI TypedDicts, and opens or refreshes an `automation/model-update` PR with a drift report. Companion scripts in `bin/drift/`: `check_model_drift.py` (provider model diff), `refresh-llms.sh` (local end-to-end refresh), `pr.sh` (open-or-refresh/close-stale PR helpers).
- **New model IDs** across all providers (first automated drift run):
  - OpenAI: `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.4-nano`
  - Gemini: `gemini-3-pro-preview`, `gemini-3.1-flash-lite`, `gemini-3.1-flash-lite-preview`, `gemini-flash-latest`, `gemini-flash-lite-latest`, `gemini-pro-latest`
  - Mistral: `devstral-medium-latest`, `ministral-14b-latest`, `mistral-medium`, `mistral-medium-3`, `mistral-medium-3.5`, `mistral-tiny-latest`, `codestral-embed`, `voxtral-mini-realtime-latest`, `voxtral-mini-tts-latest`, `voxtral-small-latest`
  - Grok: `grok-3-fast`, `grok-3-mini-fast`, `grok-4-1-fast`, `grok-4.20`, `grok-4.20-non-reasoning`, `grok-4.20-reasoning`, `grok-4.3`, `grok-code-fast`, and `-latest` aliases for Grok 3/4 families

### Chore

- Bump SDK floors: `openai>=2.36.0`, `google-genai>=2.1.0`, `xai-sdk>=1.12.2`, `mcp>=1.27.1`
- Move `google-genai`, `mcp`, `openai`, `xai-sdk` into a dedicated `[dependency-groups.llms]` (enumerable by the drift workflow)
- Scope pyright to `padwan_ai` and `tests` to avoid OOM on transitive SDK sources

## 0.6.0 (2026-05-02)

### Feat

- **mcp**: add `McpStreamable` (HTTP) and `McpStdio` (subprocess) transports implementing the [MCP 2025-11-25 spec](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports), with tool discovery, bearer auth, session management, ping, progress notifications, request cancellation, and in-place tool refresh on `notifications/tools/list_changed`
- **agent** *(alpha)*: add `AgentSession` — multi-turn agentic loop with streaming, sequential/parallel tool execution, approval hooks, error handlers, tool-result truncation, and snapshot persistence via `ConversationStore`. Per-round tool refresh picks up MCP `tools/list_changed` without restarting the session. Automatic tool namespacing on collision via `auto_prefix`, with startup rollback on partial initialization failure
- **thoughts**: unified `on_thought` callback across Gemini, Grok, and Mistral for streaming model reasoning tokens separately from the final answer
- **gemini**: thinking models support (`thinkingConfig`, `thinkingBudget`) with thought/answer separation in both streaming and non-streaming paths
- support Python 3.13 (`requires-python >= 3.13`)

### Refactor

- replace manual SSE line parsing in OpenAI and Gemini streaming with niquests native SSE extension (`resp.extension`)
- Use `orjson` when available
- **docs**: migrate from mkdocs-material to [zensical](https://github.com/polarsen-io/zensical)

### Fix

- thought tokens leaking into `complete_chat` text output on Gemini
- empty SSE `data:` frames (keep-alives) treated as malformed JSON
- OpenAI/Grok SSE responses missing `charset` in `Content-Type` causing `TypeError` on stream iteration

### Dependencies

- bump niquests to `>=3.18.5`
- bump urllib3-future to `>=2.19.905`

### Agent alpha limitations

The `AgentSession` API is functional but considered alpha — the interface may change in future releases. Known limitations:

- No mid-stream approval — `approve_tool` runs after all tool calls for a round are known, not as they arrive
- Tool results are string-only — MCP image/resource content blocks are JSON-serialized
- No per-call cancellation — you can cancel the whole `send()`/`stream()` task, but not an individual in-flight tool call
