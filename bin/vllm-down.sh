#!/usr/bin/env bash
# DESCRIPTION
#   Stop and remove the local vLLM container started by bin/vllm-up.sh.
#
# USAGE
#   ./bin/vllm-down.sh

set -euo pipefail

docker rm -f padwan-vllm >/dev/null 2>&1 || true
