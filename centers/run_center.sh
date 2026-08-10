#!/bin/bash
# Generic center runner. Usage: ./run_center.sh <center-name>
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="/root/.opencode/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
NAME="${1:?center name required}"
PROMPT_FILE="centers/$NAME/prompt.md"
if [ ! -f "$PROMPT_FILE" ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) ERROR: no prompt $PROMPT_FILE" >> "centers/$NAME/$NAME.log" 2>/dev/null || true
  exit 1
fi
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $NAME started" >> "centers/$NAME/$NAME.log"
python3 llm.py "$(cat "$PROMPT_FILE")" >> "centers/$NAME/$NAME.log" 2>&1 \
  || echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $NAME failed" >> "centers/$NAME/$NAME.log"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $NAME complete" >> "centers/$NAME/$NAME.log"
