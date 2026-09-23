#!/usr/bin/env bash
# DESCRIPTION
#   Run e2e tests instrumented through the Langfuse adapter, using the seeded dev project keys.
#
# USAGE
#   ./bin/observability/e2e-langfuse.sh [ENV_FILE] [PYTEST_ARGS...]
#
# EXAMPLES
#   ./bin/observability/e2e-langfuse.sh .env -k gemini

set -euo pipefail
cd "$(dirname "$0")/../.."

set -a && source bin/observability/langfuse.env && set +a
export LANGFUSE_BASE_URL=http://localhost:3001
export LANGFUSE_PUBLIC_KEY=$LANGFUSE_INIT_PROJECT_PUBLIC_KEY
export LANGFUSE_SECRET_KEY=$LANGFUSE_INIT_PROJECT_SECRET_KEY
env_file=${1:-.env}
shift || true
exec uv run pytest tests/e2e/ -m e2e --env-file "$env_file" --langfuse "$@"
