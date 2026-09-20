#!/usr/bin/env bash
# DESCRIPTION
#   Benchmark import times for padwan_ai (facade, single provider, otel).
#   Times are normalised by bare interpreter startup and rescaled to a
#   reference runner, so a slow machine scales both and cancels out.
#
# USAGE
#   ./bin/bench-imports.sh              # Pretty-print results
#   ./bin/bench-imports.sh --json       # JSON for github-action-benchmark
#   ./bin/bench-imports.sh --profile    # Top offenders via python -X importtime
#
# EXAMPLES
#   RUNS=20 ./bin/bench-imports.sh
#   ./bin/bench-imports.sh --json --label 3.13   # prefix names with the version
#   PY=.venv/bin/python ./bin/bench-imports.sh   # benchmark a specific venv
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

# Interpreter startup on a GitHub runner; only rescales the reported ms
REF_STARTUP_MS="${REF_STARTUP_MS:-23}"

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

PREFIX=${LABEL:+$LABEL · }

for cmd in uv jq; do
    command -v "$cmd" >/dev/null || { echo "Missing required tool: $cmd" >&2; exit 1; }
done
if [[ $MODE != profile ]] && ! command -v hyperfine >/dev/null; then
    echo "Missing required tool: hyperfine (https://github.com/sharkdp/hyperfine)" >&2
    exit 1
fi

# Resolve the venv interpreter once so uv startup is not part of the measurement.
# A preset PY skips it: uv run would re-add the default groups to a lean env.
PY="${PY:-$(uv run --frozen python -c 'import sys; print(sys.executable)')}"

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
    jq --arg c "$CONTROL" --arg prefix "$PREFIX" \
        --argjson base "$BASE" --argjson ref "$REF_STARTUP_MS" '
        [.results[] | select(.command != $c) | {
            name: ($prefix + .command),
            unit: "ms",
            value: (.mean / $base * $ref * 100 | round / 100),
            range: (.stddev / $base * $ref * 100 | round / 100)
        }]' "$RESULTS"
else
    printf "\n📊 Import Benchmark Results (startup here: %.2fms, normalised to %sms):\n" \
        "$(jq -n --argjson b "$BASE" '$b * 1000')" "$REF_STARTUP_MS"
    printf "============================================================\n"
    jq -r --arg c "$CONTROL" --argjson base "$BASE" --argjson ref "$REF_STARTUP_MS" \
        '.results[] | select(.command != $c) | [.command, (.mean / $base * $ref), (.stddev / $base * $ref)] | @tsv' "$RESULTS" \
        | while IFS=$'\t' read -r name mean std; do
            printf "  %-30s %9.2fms (±%.2fms)\n" "$name" "$mean" "$std"
        done
    printf "============================================================\n"
fi
