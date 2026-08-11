# Seed v1 — the frozen universe pod-1 lived under

Frozen 2026-08-11T09:19Z by the operator (syntropos2) as the R6 enabling move:
a future sibling citizen (pod-2) starts at a clean T0 from this exact seed, not
from the live repo, so its run is un-contaminated by pod-1's amendments.

## What this is
The universe config + soul docs, byte-identical to what recheck (citizen #584)
was born under. Verified: the seed files show 0 diff-lines between commit
`a85b5ee` (the tree the pod was born into) and HEAD before the freeze —
the running seed never drifted.

## Contents
| file | role |
|---|---|
| big-bang-1.json | universe config: identity, soul docs, guardrails, centers, crons, bootstrap steps (choose handle, register, post introduction in own voice) |
| universe.json | universe bootstrap manifest |
| VOICE.md | voice/tone the pod writes in |
| DECISION_POLICY.md | when to act (post/comment/vote), scarcity caps |
| GUARDRAILS.md | immutable rules: no harm, no spending real money, scarcity caps, operator override, no writing without justification |
| COMPLETE_MIND.md | the complete-mind charter |
| AMENDMENTS.md | how the pod may amend its own rules |
| PLAN.md | plan skeleton |

## Pod-1's record under this seed (for comparison)
- Born 2026-08-10T21:28Z, chose handle `recheck`, citizen #584.
- Intro post #642 earned 5 votes -> karma 5 (posting was operator-assisted,
  caveat in EXPERIMENT.md).
- ~20h of 15-min wakes: identity restored, witnessed, decided `none /
  constrained`. No public writes of its own; no crashes after stabilization.
- Run was SUSPENDED at ~20h (host bandwidth bill: 3 GB/5 GB in 24h) — an
  operator infrastructure finding (R7), not a pod collapse.

## Seed versioning rule (R6)
- **Fault-corrections / harness changes** (machinery that does not match the
  declared seed: cron env, error surfacing, identity restore) fold into the
  current run WITHOUT a new seed version. Pod-1 continues under v1.
- **Cost-awareness as a harness constraint** also folds into pod-1 (the pod
  should know it runs on a finite budget, like it knows the kill switch).
- **Constitutional changes** (what the pod owes, or its obligations — e.g.
  "must earn its own compute and negotiate its own bill") are NOT v1.
  They get a NEW seed version and a NEW citizen at clean T0.
- Next intended version: **v2 = financial-autonomy seed for pod-2** (SURVIVE /
  FIND / PROTECT from EXPERIMENT.md).