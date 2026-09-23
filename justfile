set quiet

# List available recipes
default:
    @just --list


# Run unit tests
[group('dev')]
test *args:
    uv run pytest {{ args }}

# Run unit tests on the lowest supported Python (matches CI matrix floor)
[group('dev')]
test-min *args:
    uv run --python 3.13 pytest {{ args }}

# Run e2e tests (copy env.template to .env first, then fill in keys)
[group('dev')]
e2e env=".env" *args:
    uv run pytest tests/e2e/ -m e2e --env-file {{ env }} {{ args }}

# Local observability stacks (OTel, Langfuse): just obs::<tab>
mod obs "bin/observability"

vllm_model := env("VLLM_MODEL", "Qwen/Qwen3-0.6B")

# Start a local vLLM server on :8100 (Docker, NVIDIA GPU, reasoning parser on)
[group('vllm')]
vllm-up:
    ./bin/vllm-up.sh {{ vllm_model }}

# Stop and remove the local vLLM server
[group('vllm')]
vllm-down:
    ./bin/vllm-down.sh

# Run vLLM e2e tests against the local server
[group('vllm')]
e2e-vllm *args: vllm-up
    VLLM_BASE_URL=http://localhost:8100/v1 VLLM_MODEL={{ vllm_model }} uv run pytest tests/e2e/test_vllm.py -m e2e {{ args }}

# Type check
[group('dev')]
check:
    uv run pyright padwan_ai/

# Lint
[group('dev')]
lint:
    uv run ruff check padwan_ai/ tests/

# Format
[group('dev')]
fmt:
    uv run ruff format padwan_ai/ tests/

# Fix lint issues where possible
[group('dev')]
fix:
    uv run ruff check --fix padwan_ai/ tests/
    uv run ruff format padwan_ai/ tests/

# Lint + type check + test
[group('dev')]
ci: lint check test

# Benchmark import times (add --profile for a per-module breakdown)
[group('dev')]
bench-imports *args:
    ./bin/bench-imports.sh {{ args }}

# Serve docs locally with hot reload
[group('docs')]
docs port="8000":
    uv run --group docs zensical serve -f zensical.toml -a localhost:{{ port }}

# Build docs
[group('docs')]
docs-build:
    uv run --group docs zensical build -f zensical.toml

# Regenerate OpenAI TypedDict types from upstream spec
[group('gen')]
gen-openai:
    ./bin/gen-openai-types.sh

# Regenerate Mistral TypedDict types from upstream spec
[group('gen')]
gen-mistral:
    ./bin/gen-mistral-types.sh

# Regenerate all provider types
[group('gen')]
gen-all: gen-openai gen-mistral

# Regenerate docs/static/favicon.png (64x64) from the full-resolution logo
[group('gen')]
gen-favicon:
    uv run --with pillow python -c "from PIL import Image; Image.open('docs/static/logo-hood.png').resize((64, 64), Image.Resampling.LANCZOS).save('docs/static/favicon.png', optimize=True)"
    echo "regenerated docs/static/favicon.png"

# Bump version (commitizen — updates pyproject.toml and CHANGELOG)
[group('release')]
bump *args:
    uv run --group bump cz bump {{ args }}
