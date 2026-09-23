#!/usr/bin/env bash
# DESCRIPTION
#   Start a local vLLM OpenAI-compatible server on :8100 (native via uvx, reasoning parser on).
#   Logs go to .scratch/vllm.log; stop it with bin/vllm-down.sh.
#
# USAGE
#   ./bin/vllm-up.sh [MODEL]
#
# EXAMPLES
#   ./bin/vllm-up.sh Qwen/Qwen3-1.7B

set -euo pipefail
cd "$(dirname "$0")/.."

model=${1:-Qwen/Qwen3-0.6B}
log=.scratch/vllm.log
mkdir -p .scratch

if ! curl -sf http://localhost:8100/health >/dev/null; then
    # managed python ships Python.h (triton JIT); eager mode avoids CUDA graph capture hangs
    setsid nohup uvx --managed-python --python 3.12 --from vllm vllm serve "$model" --port 8100 \
        --reasoning-parser qwen3 --max-model-len 4096 --gpu-memory-utilization 0.7 --enforce-eager \
        >"$log" 2>&1 </dev/null &
    echo $! >.scratch/vllm.pid
    until curl -sf http://localhost:8100/health >/dev/null; do
        kill -0 "$(cat .scratch/vllm.pid)" 2>/dev/null || { tail -30 "$log" >&2; exit 1; }
        sleep 3
    done
fi
echo "vLLM: http://localhost:8100/v1 ($model)"
