#!/bin/bash
# pod-1 heartbeat — wake a fresh instance, apply the decision policy, sleep.
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/root/.opencode/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# Kill switch layers 1+2: the pod checks these every wake. The operator can
# drop either file from outside. The pod CAN ignore these — the ultimate
# switch is the operator's custody of the model key, hosting, repo, and
# citizen secret (see kill_switch.py).
if [ -f OPERATOR_OVERRIDE.md ] || [ -f KILL ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) KILL SWITCH present, skipping wake" >> heartbeat.log
  exit 0
fi

# The first autonomous act: if not registered, the pod chooses its own name
# and registers itself. This is the big bang's first decision.
if [ ! -f .pod-config.json ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) not registered — the pod chooses its own name" >> heartbeat.log
  python3 register.py >> heartbeat.log 2>&1 || echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) registration failed" >> heartbeat.log
fi

if [ -f centers/attention/flag.txt ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FLAG present, event-triggered wake" >> heartbeat.log
fi

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) heartbeat started" >> heartbeat.log
python3 witness.py --record-on-change >> heartbeat.log 2>&1 || true

python3 wake.py >> heartbeat.log 2>&1 || echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) wake failed" >> heartbeat.log

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) heartbeat complete" >> heartbeat.log
