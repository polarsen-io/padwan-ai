# AGENTS.md

Padwan AI: lightweight async client library for OpenAI, Gemini, Mistral, Grok, Anthropic, Voyage and any
OpenAI-compatible API. `LLMClient` (`padwan_ai/client.py`) is the facade that dispatches on model name to a provider
client (`padwan_ai/<provider>/client.py`, subclassing `LLMClientBase` in `padwan_ai/_base.py`). `AgentSession`
(`padwan_ai/agent.py`) is the tool-calling loop on top. `TypeSafeClient` (`padwan_ai/typesafe/`, experimental) is
standalone: not a `LLMClientBase` subclass and not routed by `LLMClient`.

Setup, workflow, PR and release conventions: see `CONTRIBUTING.md`.

## Stack

- Python >=3.13 (CI: 3.13, 3.14, 3.15), uv, ruff, pyright, pytest + pytest-asyncio (`asyncio_mode = "auto"`), just.
- HTTP via `niquests` only; payloads are `TypedDict`s. No provider SDKs at runtime: the `llms` dependency group
  (openai, anthropic, google-genai, ...) is for tests, type cross-checks and drift checks only. Never add a runtime
  dependency.
- Import time is benchmarked in CI (`just bench-imports`); keep provider imports lazy and keep the
  `__lazy_modules__` declarations in `padwan_ai/__init__.py` and `padwan_ai/client.py` (effective on 3.15+).

## Verify

Match CI, which is wider than the `just lint`/`just check` recipes:

```bash
uv sync --all-extras --all-groups
uv run ruff check . && uv run ruff format --check .   # also formats Python code blocks in docs/*.md
uv run pyright                                        # includes tests/
uv run pytest                                         # e2e excluded by default
just test-min                                         # same suite on 3.13, the supported floor
```

E2E needs real keys: `cp env.template .env`, then `just e2e` (`just e2e-vllm` needs a local GPU). For OpenTelemetry
changes, run e2e with `--otel`: it fails on span attributes the docs don't name.

## Rules linters don't catch

- Supported floor is 3.13: native generics (`class Foo[T]`) are fine, but no PEP 649 — use
  `from __future__ import annotations` where forward references need it.
- Generated, never hand-edit: `padwan_ai/openai/types.py`, `padwan_ai/mistral/types.py` (`just gen-all`) and
  `padwan_ai/mistral/_deprecations.py` (`bin/drift/check_model_drift.py`). Put custom TypedDicts in the relevant
  module (e.g. `padwan_ai/openai/batch.py`).
- Annotate `_check_resp()` results and `json=` payloads with their TypedDict
  (`data: BatchResponse = _check_resp(resp)`).
- No `assert` for runtime checks. Provider/API failures raise from `padwan_ai/errors.py`; keep existing `ValueError`
  (bad arguments) and `RuntimeError` (lifecycle misuse) contracts.
- Tests: `pytest.param(..., id="...")` for every parametrized case; mock HTTP in unit tests, real calls only under
  `tests/e2e/` with `@pytest.mark.e2e`.
- Model `Literal`s (`OpenAIModel`, `GeminiModel`, ...) live in each provider's `client.py`; add stable aliases only,
  never dated snapshots, and don't remove IDs without a human-reviewed deprecation.
- A weekly refresh (`.github/workflows/model-drift.yml`, Mondays 09:00 UTC, `bin/drift/refresh-llms.sh`) bumps the
  `llms` group, regenerates types and, when anything changed, opens or refreshes a PR with a model drift report.
  Don't hand-bump those in unrelated PRs.
- User-facing changes update `docs/` (including the provider matrices) and `README.md` when relevant.
