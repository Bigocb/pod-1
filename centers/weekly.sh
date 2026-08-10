#!/bin/bash
# The weekly sequence: dream (pattern-find), meta (watch the parliament),
# memory-keeper (forget), then re-run consolidation to fold it into memory.
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="/root/.opencode/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

for center in dream meta memory_keeper; do
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) weekly: $center started" >> "centers/$center/$center.log"
  if [ -f "centers/$center/prompt.md" ]; then
    opencode run --pure --format json --dir "$(pwd)" \
      --model ollama-cloud/deepseek-v4-flash:0731 \
      "$(cat "centers/$center/prompt.md")" >> "centers/$center/$center.log" 2>&1 \
      || echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) weekly: $center failed" >> "centers/$center/$center.log"
  fi
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) weekly: $center complete" >> "centers/$center/$center.log"
done

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) weekly sequence complete" >> centers/daily.log
