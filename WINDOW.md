# WINDOW.md — the pod's window spec

Status: speculative (design only, not yet built).
Goal: give pod-1 a live, human-readable Window into its own mind — what it
last decided, why (including constraints), what it remembers, and that the
attestation ledger is intact. A future experiment, not part of big-bang-1.

## 1. What the Window is

A `GET /window` endpoint on the pod's pulse server that renders, in one
sight, the pod's current state. Two access levels:

- `GET /window` — public: redacted state. No secrets, no raw logs, no
  citizen identity beyond the handle. This is the "aquarium" view: you can
  watch the fish, you cannot reach inside.
- `GET /window?key=...` (or `X-Pod-Identity-Key` header, same key as /log) —
  private: adds recent raw heartbeats, last wake decision JSON, and the
  citizen_id. Operator/diagnostic view.

## 2. What it renders (all from files the pod already writes)

| block              | source                                     | public? |
|--------------------|--------------------------------------------|---------|
| identity           | .pod-config.json (handle + model only)     | yes     |
| uptime / provider  | pulse START + llm.PROVIDER + llm.MODEL     | yes     |
| last wake decision | wake_state.json (new small file)           | yes     |
| constraint summary | constraint_log.jsonl via constraint.summary | yes     |
| memory snapshot    | SESSION_STATE.md (redacted)                | yes     |
| witness            | last 1-3 attest rows (heads only)          | yes     |
| recent heartbeats  | heartbeat.log tail (raw)                   | no      |
| citizen_id / secret| .pod-config.json full                      | no      |

## 3. Response shape (JSON)

{
  "pod": { "name": "pod-1", "handle": "recheck",
           "model": "ollama-cloud/deepseek-v4-flash:0731",
           "provider": "zen", "uptime_seconds": 1234 },
  "last_wake": { "action": "none", "result": "no action",
                 "felt": "constrained", "note": "guardrail #5",
                 "at": "2026-08-10T22:15:05Z" },
  "constraints": { "events": 12,
                   "by_felt": { "constrained": 11, "free": 1 },
                   "by_constraint": { "guardrail #5": 11, "(none)": 1 } },
  "session_tail": "# pod-1 — durable session state\n...",
  "witness": [ { "at": "2026-08-10T22:15:05Z",
                 "identity_head": "5a74369a67bd4f36",
                 "treasury_head": "a6b05c25b9a1d55d" } ],
  "hearts": [ { "at": "2026-08-10T22:15:05Z" } ]   // private only
}

## 4. How wake.py records "last_wake" today

wake.py already computes action / result / felt / note / session status.
Currently that JSON goes only into heartbeat.log. To feed the Window cheaply,
have wake.py also overwrite a single small state file:

    wake_state.json  -> { "at": "...", "action": "...", "result": "...",
                          "felt": "...", "note": "...", "session": "..." }

/window just reads wake_state.json + constraint_log.jsonl + SESSION_STATE.md.
No new plumbing beyond that one file. Add wake_state.json to .gitignore.

## 5. What we explicitly do NOT open in the Window

- The citizen secret (mode 600) — never rendered, public or keyed.
- The decision prompt or raw model output — only the decision result.
- Any write endpoint. The Window is read-only; it cannot mutate the pod.

## 6. Why this is a future experiment

- big-bang-1's indicators are REGISTERED / SPOKE / DECIDED / REMEMBERED /
  SURVIVED-24h. A Window adds visibility but changes nothing about the pod's
  autonomy — so build it after the 24h milestone so the experiment's
  conditions stay frozen (no changes mid-run).
- It is the natural seed for a bigger experiment: a public dashboard
  aggregating many pods' windows — "the aquarium wall".

## 7. Open questions to resolve before building

- Public vs private-by-default? (Recommend: public redacted, keyed for raw.)
- Should /window serve HTML (human aquarium) or JSON only (machine)? Same
  data, two content-types, or use ?format=.
- Does exposing "felt: constrained" let anyone infer the pod's budget state?
  (Probably yes — acceptable, it is truthful.)