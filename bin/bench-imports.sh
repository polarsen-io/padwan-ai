#!/usr/bin/env bash
# DESCRIPTION
#   Benchmark import times for padwan_ai (facade, single provider, otel).
#   Results are reported relative to bare interpreter startup, so a slow CI
#   runner scales both and cancels out.
#
# USAGE
#   ./bin/bench-imports.sh              # Pretty-print results
#   ./bin/bench-imports.sh --json       # JSON for github-action-benchmark
#   ./bin/bench-imports.sh --profile    # Top offenders via python -X importtime
#
# EXAMPLES
#   RUNS=20 ./bin/bench-imports.sh
#   ./bin/bench-imports.sh --json --label 3.13   # suffix names with the version
#
# Requires: hyperfine, jq, uv

set -euo pipefail

export LC_NUMERIC=C

WARMUP="${WARMUP:-3}"
RUNS="${RUNS:-10}"
MODE=pretty
LABEL=

# Baseline command: whatever makes it slower makes the imports slower too
CONTROL="interpreter startup"

while [[ $# -gt 0 ]]; do
    case $1 in
        --json) MODE=json; shift ;;
        --profile) MODE=profile; shift ;;
        --warmup) WARMUP="$2"; shift 2 ;;
        --runs) RUNS="$2"; shift 2 ;;
        --label) LABEL="$2"; shift 2 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

SUFFIX=${LABEL:+ [$LABEL]}

for cmd in uv jq; do
    command -v "$cmd" >/dev/null || { echo "Missing required tool: $cmd" >&2; exit 1; }
done
if [[ $MODE != profile ]] && ! command -v hyperfine >/dev/null; then
    echo "Missing required tool: hyperfine (https://github.com/sharkdp/hyperfine)" >&2
    exit 1
fi

# Resolve the venv interpreter once so uv startup is not part of the measurement
PY=$(uv run --frozen python -c 'import sys; print(sys.executable)')

if [[ $MODE == profile ]]; then
    echo "Top cumulative import times for 'import padwan_ai' (µs):"
    "$PY" -X importtime -c "import padwan_ai" 2>&1 \
        | grep "^import time:" \
        | sort -t'|' -k2 -rn \
        | head -20
    exit 0
fi

RESULTS=$(mktemp)
trap 'rm -f "$RESULTS"' EXIT

hyperfine --warmup "$WARMUP" --min-runs "$RUNS" \
    --export-json "$RESULTS" \
    -n "$CONTROL" "$PY -c pass" \
    -n "padwan_ai (facade)" "$PY -c 'import padwan_ai'" \
    -n "padwan_ai.openai" "$PY -c 'from padwan_ai.openai import OpenAIClient'" \
    -n "padwan_ai.otel" "$PY -c 'import padwan_ai.otel'" \
    >/dev/null 2>&1

BASE=$(jq --arg c "$CONTROL" '.results[] | select(.command == $c) | .mean' "$RESULTS")

if [[ $MODE == json ]]; then
    jq --arg c "$CONTROL" --arg suffix "$SUFFIX" --argjson base "$BASE" '
        [.results[] | select(.command != $c) | {
            name: (.command + $suffix),
            unit: "x startup",
            value: (.mean / $base * 1000 | round / 1000),
            range: (.stddev / $base * 1000 | round / 1000)
        }]' "$RESULTS"
else
    printf "\n📊 Import Benchmark Results (interpreter startup: %.2fms):\n" "$(jq -n --argjson b "$BASE" '$b * 1000')"
    printf "============================================================\n"
    jq -r --arg c "$CONTROL" --argjson base "$BASE" \
        '.results[] | select(.command != $c) | [.command, (.mean * 1000), (.stddev * 1000), (.mean / $base)] | @tsv' "$RESULTS" \
        | while IFS=$'\t' read -r name mean std ratio; do
            printf "  %-30s %9.2fms (±%.2fms)  %5.2fx startup\n" "$name" "$mean" "$std" "$ratio"
        done
    printf "============================================================\n"
fi
