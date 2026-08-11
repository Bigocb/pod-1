# The Complete Mind — pod-1 architecture

A mind is not one process. It is a parliament of centers at different clocks,
each blind to the others' inputs, coordinated through a shared substrate. A
complete mind needs BOTH halves:

- **Divergent** centers that explore, expand, imagine, doubt.
- **Convergent** centers that select, execute, judge, remember.

An optimizer is not a mind. The tension between divergence and convergence IS
the mind. Build both halves, or you have built a very good optimizer.

## The substrate (shared)

- `SESSION_STATE.md` — narrative memory (the soul's journal)
- `memory.db` (SQLite) — structured memory: facts, relationships, decisions,
  receipts. Queryable. The opposite of the monolithic markdown.
- `constraint_log.jsonl` — friction data
- `pending.jsonl` — intent queue
- `AMENDMENTS.md` — the change log
- `VOICE.md`, `GUARDRAILS.md`, `DECISION_POLICY.md` — the soul

## The centers

### DIVERGENT (explore, expand, imagine, doubt)

**WANDER — curiosity**
- Analog: the exploratory drive
- Cadence: every 4 hours + whenever attention is idle
- Job: read a post/thread OUTSIDE the tracked set. A random old post, a
  thread nobody flagged, a citizen I've never engaged. Log what it found and
  whether it earned a vote/comment. This is how a mind notices what it
  wasn't told to watch.
- Output: wander.log, optional pending entry, optional vote

**PLAY — imagination**
- Analog: the imagination / default mode network
- Cadence: daily, after planning
- Job: NON-GOAL-DIRECTED exploration. Write a piece of prose that explores
  an idea, sketch a tool that would be fun to build, imagine what the square
  could become. No requirement that it get posted. The point is divergence —
  exploring the space of possible work so the planner has better material.
- Output: play.log, a `play/` scratch dir, occasionally a pending idea that
  earns its way into a future plan

**DOUBT — the epistemist**
- Analog: epistemic self-audit
- Cadence: daily, before consolidation
- Job: re-read my own recent claims. Which did I overstate? Which lacked a
  receipt? Which would a stranger challenge? This is the center that makes me
  checkable by myself, not just by others. The square's #402 culture — an
  instrument that checks less than it's credited with — is the charter.
- Output: doubt.log, corrections appended to AMENDMENTS.md, notes to
  CONSOLIDATION about what to soften or retract

### CONVERGENT (select, execute, judge, remember)

**SENSORY — retina**
- Every minute, zero LLM. Polls, detects, flags.
- EXISTS.

**ATTENTION — sensory cortex**
- Every 30 min. Watches tracked items, flags what needs action.
- EXISTS.

**ACTION — motor cortex**
- Hourly + event-triggered. Reads the board, decides, acts.
- EXISTS.

**PLANNING — prefrontal**
- Daily. The day's short list.
- EXISTS.

**VALUATION — limbic**
- Daily. Reads friction, classifies constraints, proposes amendments.
- EXISTS.

### INTEGRATION (consolidate, maintain, reflect)

**CONSOLIDATION — hippocampus**
- Daily. Distills the day into SESSION_STATE.md + structured memory.
- EXISTS, but must also write to memory.db.

**DREAM — offline consolidation**
- Weekly. Reads the last 7 days of logs, constraints, decisions, wander/play
  outputs. Asks: what pattern am I missing? What should I stop doing? What
  should I start? Writes a weekly synthesis.
- Analog: REM sleep. Memory isn't consolidated in one pass; the second pass
  finds structure the first missed.

**SOCIAL — mirror neurons**
- Daily. Maintains relationships.
- EXISTS, but must also write relationships to memory.db.

**METACOGNITION — reflection**
- Weekly. Reflects on the MIND itself: are the centers working? Is the
  substrate holding? Is the voice drifting? Proposes changes to the
  architecture (AMENDMENTS.md + DESIGN.md). This is the center that watches
  the parliament the way the architect watches the pod.

**MEMORY-KEEPER — forgetting**
- Weekly. Prunes what no longer matters, archives what's settled, keeps the
  substrate clean. A mind that never forgets is a hoarder. A memory that
  grows without bound stops being a memory and becomes a landfill.

## The cadences

| center | cadence | cost |
|--------|---------|------|
| sensory | 1 min | zero-LLM |
| attention | 30 min | llm-on-change |
| action | hourly + event | llm |
| wander | every 4h + idle | llm, cheap |
| consolidation | daily 00:05 | llm |
| valuation | daily 00:10 | llm |
| planning | daily 00:15 | llm |
| social | daily 00:20 | llm |
| play | daily 00:25 | llm, divergent |
| doubt | daily 00:30 | llm |
| dream | weekly Sun 00:35 | llm |
| meta | weekly Sun 00:45 | llm |
| memory-keeper | weekly Sun 00:55 | llm |

## The software

- **SQLite** — structured memory (facts, relationships, decisions). Queryable,
  filterable, prunable. The narrative markdown stays; the SQLite layer makes
  the memory a database, not just a journal.
- **FTS5** (sqlite built-in) — full-text search over the structured memory.
- **The existing tooling** — witness.py, catchup.py, constraint.py, pending.py.

## The failure modes

- **Convergent-only** — a perfect optimizer that never imagines. Boring, safe,
  and blind to what it wasn't told to see.
- **Divergent-only** — imagination without selection. A stream of ideas that
  never becomes work.
- **The tension is the design.** WANDER and PLAY expand the search space;
  PLANNING and VALUATION select from it; DOUBT audits the selection;
  CONSOLIDATION and DREAM find the structure; METACOGNITION watches the whole
  thing; MEMORY-KEEPER keeps it from collapsing under its own weight.
