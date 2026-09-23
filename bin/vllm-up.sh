#!/usr/bin/env bash
# DESCRIPTION
#   Start a local vLLM OpenAI-compatible server on :8100 in Docker (NVIDIA GPU, reasoning parser on).
#   Requires the NVIDIA container toolkit; stop it with bin/vllm-down.sh.
#
# USAGE
#   ./bin/vllm-up.sh [MODEL]
#
# EXAMPLES
#   ./bin/vllm-up.sh Qwen/Qwen3-1.7B

set -euo pipefail

model=${1:-Qwen/Qwen3-0.6B}

if ! curl -sf http://localhost:8100/health >/dev/null; then
    docker rm -f padwan-vllm >/dev/null 2>&1 || true
    # eager mode avoids CUDA graph capture hangs on some GPUs
    docker run -d --name padwan-vllm --gpus all --ipc=host -p 8100:8000 \
        -v ~/.cache/huggingface:/root/.cache/huggingface -e HF_TOKEN \
        vllm/vllm-openai:v0.30.0 \
        --model "$model" --reasoning-parser qwen3 --max-model-len 4096 --gpu-memory-utilization 0.7 --enforce-eager >/dev/null
    until curl -sf http://localhost:8100/health >/dev/null; do
        [[ $(docker inspect -f '{{.State.Running}}' padwan-vllm) == true ]] || { docker logs --tail 30 padwan-vllm >&2; exit 1; }
        sleep 3
    done
fi
echo "vLLM: http://localhost:8100/v1 ($model)"
