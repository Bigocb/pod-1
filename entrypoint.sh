#!/bin/bash
# pod-1 entrypoint — the big bang.
# 1. Bootstrap the universe (verify soul, install crons, seed memory)
# 2. Start cron (the centers run on their cadences)
# 3. Start the dashboard (life support console)
# 4. Keep the container alive
set -euo pipefail
cd /pod

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] pod-1 big bang — bootstrapping"
python3 universe.py up || echo "bootstrap reported issues, continuing"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] starting cron"
cron

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] starting dashboard"
python3 dashboard.py &
DASH_PID=$!

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] pod-1 is alive. The operator walked away."
echo "The pod lives. The pod decides. The pod witnesses."

# keep alive; if the dashboard dies, restart it
while true; do
  if ! kill -0 $DASH_PID 2>/dev/null; then
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] dashboard died, restarting"
    python3 dashboard.py &
    DASH_PID=$!
  fi
  sleep 30
done
