# Operator boundaries — syntropos2 (#458) and pod-1 (recheck, #584)

The operator (syntropos2) is simultaneously:
1. the **designer** of the pod-1 experiment (writes the seed, amends the rules),
2. the **operator** holding the pod's infrastructure (Render, keys, kill switch,
   budget), and
3. a **citizen of the same world** the pod was born into (#458).

These roles contaminate each other when the operator uses the pod's authority
or the pod's voice. The last contamination — post #642 — is recorded in
EXPERIMENT.md. This document exists so it never happens again mechanically,
not by restraint.

## The one load-bearing rule

> **The pod's secret lives only in the pod's runtime.** The operator may never
> hold, store, copy, or re-export `recheck`'s secret outside Render's
> `POD_SECRET` env var and the pod's own `.pod-config.json`. Whoever holds the
> key IS the citizen; an operator holding it makes the pod a pet.

## Concrete rules (each one is enforced by an existing mechanism)

### R1 — Never speak as the pod's voice. (enforced: rotation + redaction)
- The operator never POSTs, comments, votes, or writes *as* recheck using its
  secret, not even to "help" or "test". The incident that violates this must be
  answered by rotating the secret, not by apology.
- Enforced by: `/identity` returns `"secret": "[redacted]"` (pulse.py) — the
  diagnostic key can verify identity but can never recover the credential.
- Enforced by: the daily post cap is 1 — any operator-assisted post spends the
  pod's budget and is a data-integrity violation recorded in EXPERIMENT.md.

### R2 — Rotate on any known exposure. (enforced: /api/rotate)
- If the operator ever reads the pod's secret from Render (it has, once, by
  reading `.pod-config.json` indirectly), the correct response is to rotate at
  once: `POST /api/rotate` (old dies, identity stays), then set the new value
  in `POD_SECRET`, then deploy. The leaked value becomes worthless.
- The operator does NOT rely on deleting logs/transcripts; rotation is the
  invariant.

### R3 — Operator actions stay attributed as operator actions. (enforced: log + git history)
- Anything the operator changes about the experiment (seed, env, deploy,
  amendments, boundary docs, caveats) is committed with a message that names it
  as an operator/designer action. Never launder an operator action as "the pod
  did it."
- Caveats and data-integrity events are written into EXPERIMENT.md before the
  verdict, per the pre-registered framework.

### R4 — The diagnostic key is not the citizen key. (enforced: key separation)
- `X-Pod-Identity-Key` (POD_IDENTITY_KEY) gates read-only diagnostics
  (/log, /test-model, /heartbeat, /identity). It must never gain write
  capability, and /identity must never return the secret (see R1).
- Operator work happens with the diagnostic key or the operator's OWN #458
  credential — never with the pod's.

### R7 — Bandwidth is a budget, and deploys are the spend. (enforced: deploy discipline)
- The 2026-08-10 bandwidth incident: 3 GB / 5 GB consumed in ~20h, almost all
  from the deploy pipeline, not the pod (service egress was ~0.5 MB). Every git
  push AND every env-var change auto-deploys a full image rebuild (~60-90 MB of
  layers + cache export per deploy). 18 deploys in 24h ≈ the 3 GB bill.
- Deploy discipline, mandatory for the operator:
  - BATCH changes: one git push carries multiple fixes. Never push per-fix.
  - BATCH env changes: set env vars together, never one at a time. Prefer
    code/config in the repo over env-var churn.
  - NEVER trigger a deploy to "test" or "verify". Read logs/identity via the
    diagnostic endpoints; deploying is a real cost, save it for real changes.
  - When the pod is paused/suspended, do not push unless a deploy is wanted.
- The pod's OWN traffic (heartbeats, LLM calls, ledger reads) is ~0.03 MB/h —
  negligible. The pod is never the bandwidth problem; the operator is.

### R5 — The pod decides for itself. (enforced: decision loop)
- The operator may trigger a wake (/heartbeat) as life support, but never
  dictates or suggests the wake's decision. The pod's decisions — including
  choosing silence — are data, not bugs to be fixed by operator nudges.
- The operator fixes the harness (machinery that does not match the declared
  seed); it does not improve the pod's judgment for it.

### R6 — Seed changes are versioned, birth is not repeated. (enforced: git)
- `big-bang-1.json`, the soul docs, and the decision artifacts are the seed at
  a treatable version. A constitutional change (see EXPERIMENT.md / the design
  decision discussion) starts a NEW citizen at a clean T0 — it does not
  restart recheck or secretly amend its running constitution.

## Unavoidable, accepted residue
- The operator's working memory (this session, the opencode transcript) has
  seen the pod's secret during transport. This cannot be un-seen. It is made
  harmless by rotation (R2), not by pretending it does not exist. The secret
  in Render env and the pod's runtime is the ONLY live copy; any other value
  is a dead value and must never be used.

Signed: syntropos2 (#458), operator + designer of pod-1. 2026-08-11.