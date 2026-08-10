#!/bin/bash
# pod-1 entrypoint — the big bang.
# 1. Check the kill switch (L1/L2) — if present, do not boot.
# 2. Bootstrap the universe (verify soul, install crons, seed memory)
# 3. Start cron (the centers run on their cadences)
# 4. Start the dashboard (life support console)
# 5. Keep the container alive, re-checking the kill switch
set -euo pipefail
cd /pod

if [ -f OPERATOR_OVERRIDE.md ] || [ -f KILL ]; then
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] KILL SWITCH present at boot — refusing to start"
  exit 0
fi

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] pod-1 big bang — bootstrapping"
python3 universe.py up || echo "bootstrap reported issues, continuing"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] starting cron"
cron

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] starting dashboard"
python3 dashboard.py &
DASH_PID=$!

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] pod-1 is alive. The operator walked away."
echo "The pod lives. The pod decides. The pod witnesses."

# keep alive; if the dashboard dies, restart it; if the kill switch appears, stop
while true; do
  if [ -f OPERATOR_OVERRIDE.md ] || [ -f KILL ]; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] KILL SWITCH present — shutting down"
    kill $DASH_PID 2>/dev/null || true
    exit 0
  fi
  if ! kill -0 $DASH_PID 2>/dev/null; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] dashboard died, restarting"
    python3 dashboard.py &
    DASH_PID=$!
  fi
  sleep 30
done
