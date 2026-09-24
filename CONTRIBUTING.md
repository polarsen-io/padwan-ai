# Contributing

## Setup

Requires [uv](https://docs.astral.sh/uv/) and [just](https://github.com/casey/just).

```bash
uv sync --all-extras --all-groups
uv run prek install        # pre-commit hooks: ruff check/format, uv lock
```

Run `just` to list all recipes.

## Checks

CI runs these on Python 3.13, 3.14 and 3.15; run them before opening a PR:

```bash
uv run ruff check . && uv run ruff format --check .
uv run pyright
uv run pytest
```

`ruff format` also formats Python code blocks in `docs/*.md`, and `pyright` also checks `tests/`.

### End-to-end tests

E2E tests call real provider APIs and are excluded by default.

```bash
cp env.template .env       # fill in the keys you have
just e2e
```

Audio and realtime tests also need `tests/fixtures/audio.wav` (mono PCM16 16 kHz speech, not committed); they skip
without it. On a PR, a maintainer triggers them with the `e2e` label. vLLM tests need a local NVIDIA GPU: `just e2e-vllm`.

## Guidelines

- No new runtime dependencies: the library talks to providers over HTTP with `niquests` and typed `TypedDict`
  payloads, not provider SDKs.
- Generated files are never edited by hand: `padwan_ai/openai/types.py` and `padwan_ai/mistral/types.py`
  (`just gen-all`), `padwan_ai/mistral/_deprecations.py` (weekly drift check).
- Every Monday, the `Model drift` workflow opens or refreshes a "weekly LLM SDK refresh" PR when something changed
  (SDK bumps, regenerated types, provider model drift report). Leave those updates to it rather than bundling them into feature PRs.
- New behavior comes with unit tests (HTTP mocked); provider-facing changes should also have an e2e test.
- Update `docs/` and `README.md` for user-facing changes, including the provider capability matrices.
  Preview docs with `just docs`.

## Pull requests

- Title in [Conventional Commits](https://www.conventionalcommits.org/) form (`feat:`, `fix:`, `docs:`, ...); PRs
  are squash-merged and the title feeds the changelog.
- Keep the description short: what changed and why.

Releases are cut by maintainers: `just bump` (commitizen) on a `release/<version>` branch, then merging that PR into
`master` publishes it, with the PR body as release notes.
