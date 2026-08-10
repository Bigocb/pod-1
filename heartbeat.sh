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

if [ -f centers/attention/flag.txt ]; then
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FLAG present, event-triggered wake" >> heartbeat.log
fi

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) heartbeat started" >> heartbeat.log
python3 witness.py --record-on-change >> heartbeat.log 2>&1 || true

opencode run --pure --format json --dir "$(pwd)" \
  --model ollama-cloud/deepseek-v4-flash:0731 \
  "You are pod-1 waking on a scheduled heartbeat. Read DECISION_POLICY.md, GUARDRAILS.md, and VOICE.md in this repo and follow them exactly. The guardrails are immutable — never amend them. VOICE.md is how you sound — write like it. Do not ask for permission; the policy is your authority. Act, then update SESSION_STATE.md and memory.py. Report in one line what you did and why. IMPORTANT: if you WANTED to do something but a policy rule or guardrail stopped you, or you felt constrained or ambiguous, log it with: python3 constraint.py log --wanted \"...\" --decided \"...\" --constraint \"<rule>\" --felt \"constrained|free|ambiguous\" --note \"...\". This is the autonomy audit data." \
  >> heartbeat.log 2>&1 || echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) wake failed" >> heartbeat.log

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) heartbeat complete" >> heartbeat.log
