#!/usr/bin/env bash
# DESCRIPTION
#   Stop the local vLLM server started by bin/vllm-up.sh.
#
# USAGE
#   ./bin/vllm-down.sh

set -euo pipefail
cd "$(dirname "$0")/.."

pidfile=.scratch/vllm.pid
[[ -f $pidfile ]] || { echo "vLLM not running (no $pidfile)"; exit 0; }
# setsid made the server its own process group; kill the whole group (API server + engine core)
kill -- "-$(cat "$pidfile")" 2>/dev/null || true
rm -f "$pidfile"
