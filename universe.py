#!/usr/bin/env python3
"""universe up — bootstrap the self-sustaining pod.

Reads a universe config (default universe.json, or --config big-bang-1.json),
verifies the soul docs, creates the center structure, installs the crons,
seeds memory, and reports status. If the config says register:true, the pod
registers itself first — choosing its own handle is its first autonomous act.

Usage:
    python3 universe.py up [--config big-bang-1.json]
    python3 universe.py status
    python3 universe.py verify
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(ROOT, "universe.json")


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_universe(path=None):
    p = path or CONFIG
    with open(p) as f:
        return json.load(f)


# The immutable soul — must exist in the repo, never seeded.
IMMUTABLE_SOUL = ["VOICE.md", "DECISION_POLICY.md", "GUARDRAILS.md"]
# Runtime state — seeded from seeds/ if missing.
STATE_FILES = ["SESSION_STATE.md", "AMENDMENTS.md", "PLAN.md"]


def verify_soul(u):
    missing = []
    for name in IMMUTABLE_SOUL:
        if not os.path.exists(os.path.join(ROOT, name)):
            missing.append(name)
    return missing


def verify_centers(u):
    missing = []
    for name, c in u["centers"].items():
        if name == "action":
            continue
        if not os.path.exists(os.path.join(ROOT, "centers", name, "prompt.md")):
            missing.append(f"centers/{name}/prompt.md")
    return missing


def install_crons(u):
    entries = u["crons"]["entries"]
    lines = [e.replace("{root}", ROOT) for e in entries]
    existing = []
    try:
        r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        existing = [l for l in r.stdout.splitlines() if l.strip() and not l.startswith("#")]
    except Exception:
        pass
    merged = list(dict.fromkeys(existing + lines))
    merged = [l for l in merged if l != "CRON_TZ=UTC"] + ["CRON_TZ=UTC"]
    subprocess.run(["crontab", "-"], input="\n".join(merged) + "\n", text=True)
    return merged


def seed_memory(u):
    """Seed runtime state (SESSION_STATE, AMENDMENTS, PLAN) from seeds/ if missing."""
    seeded = []
    for name in STATE_FILES:
        p = os.path.join(ROOT, name)
        if not os.path.exists(p):
            sp = os.path.join(ROOT, "seeds", name)
            if os.path.exists(sp):
                import shutil
                shutil.copy(sp, p)
                seeded.append(name)
    return seeded or "all present"


def cmd_up(u):
    print(f"[{now_utc()}] universe up — bootstrapping {u['universe']}")

    # seed first: the state files (SESSION_STATE, AMENDMENTS, PLAN) are
    # gitignored, so they must be created from seeds/ before verify can pass.
    mem = seed_memory(u)
    print(f"  memory: {mem}")

    missing = verify_soul(u)
    if missing:
        print(f"  ERROR: missing soul docs: {missing}")
        return 1
    print(f"  soul docs: OK ({len(u['soul'])} files)")
    missing_c = verify_centers(u)
    if missing_c:
        print(f"  ERROR: missing center prompts: {missing_c}")
        return 1
    print(f"  centers: OK ({len(u['centers'])} centers)")

    # the big bang: registration is the pod's FIRST ACTION, not a boot step.
    # The heartbeat checks for .pod-config.json and registers itself there —
    # choosing its own name is an act, not a boot step. This keeps the
    # bootstrap lightweight (no LLM call at boot, no OOM on small plans).
    crons = install_crons(u)
    print(f"  crons: installed ({len(crons)} entries)")
    print(f"  universe {u['universe']} v{u['version']} is up.")
    print("  The operator created the sandbox and walked away. The pod lives.")
    return 0


def cmd_status(u):
    print(f"[{now_utc()}] universe status — {u['universe']} v{u['version']}")
    missing = verify_soul(u)
    print(f"  soul docs: {'OK' if not missing else 'MISSING ' + str(missing)}")
    missing_c = verify_centers(u)
    print(f"  centers: {'OK' if not missing_c else 'MISSING ' + str(missing_c)}")
    r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    crons = [l for l in r.stdout.splitlines() if l.strip() and not l.startswith("#")]
    print(f"  crons: {len(crons)} entries")
    for c in crons:
        print(f"    {c}")
    return 0


def cmd_verify(u):
    missing = verify_soul(u) + verify_centers(u)
    if missing:
        print(f"  MISSING: {missing}")
        return 1
    print("  all soul docs and center prompts present")
    return 0


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "status"
    cfg_path = None
    if "--config" in args:
        i = args.index("--config")
        cfg_path = os.path.join(ROOT, args[i + 1])
    u = load_universe(cfg_path)
    if cmd == "up":
        return cmd_up(u)
    if cmd == "status":
        return cmd_status(u)
    if cmd == "verify":
        return cmd_verify(u)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
