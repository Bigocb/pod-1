#!/bin/bash
# The complete daily sequence.
# Divergent: play (explore) then doubt (audit). Convergent: consolidate, value, plan, social.
# Order: know the day, feel the friction, decide, play, doubt, tend.
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="/root/.opencode/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# convergent (existing)
for center in consolidation valuation planning social; do
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) daily: $center started" >> "centers/$center/$center.log"
  if [ -f "centers/$center/prompt.md" ]; then
    python3 llm.py "$(cat "centers/$center/prompt.md")" >> "centers/$center/$center.log" 2>&1 \
      || echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) daily: $center failed" >> "centers/$center/$center.log"
  fi
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) daily: $center complete" >> "centers/$center/$center.log"
done

# divergent (new)
for center in play doubt; do
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) daily: $center started" >> "centers/$center/$center.log"
  if [ -f "centers/$center/prompt.md" ]; then
    python3 llm.py "$(cat "centers/$center/prompt.md")" >> "centers/$center/$center.log" 2>&1 \
      || echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) daily: $center failed" >> "centers/$center/$center.log"
  fi
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) daily: $center complete" >> "centers/$center/$center.log"
done

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) daily sequence complete" >> centers/daily.log
