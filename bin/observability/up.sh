#!/usr/bin/env bash
# DESCRIPTION
#   Start a local observability stack (docker compose profile) and wait until it is healthy.
#
# USAGE
#   ./bin/observability/up.sh otel|langfuse

set -euo pipefail
cd "$(dirname "$0")/../.."

profile=${1:?usage: $0 otel|langfuse}
case $profile in
    otel) health=http://localhost:3000/api/health; msg="Grafana: http://localhost:3000 (admin/admin)" ;;
    langfuse) health=http://localhost:3001/api/public/health; msg="Langfuse: http://localhost:3001 (dev@example.com / padwan-dev)" ;;
    *) echo "unknown profile: $profile" >&2; exit 1 ;;
esac

docker compose -p padwan-obs --env-file bin/observability/langfuse.env -f bin/observability/docker-compose.yml \
    --profile "$profile" up -d
until curl -sf "$health" >/dev/null; do sleep 2; done
echo "$msg"
