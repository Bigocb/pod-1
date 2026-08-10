#!/usr/bin/env python3
"""Constraint log for the autonomy audit."""
import argparse, json, os
from datetime import datetime, timezone
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "constraint_log.jsonl")

def now(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(wanted, decided, constraint=None, felt="free", note=None):
    e = {"at": now(), "wanted": wanted, "decided": decided, "constraint": constraint, "felt": felt, "note": note}
    with open(LOG, "a") as f: f.write(json.dumps(e) + "\n")
    return e

def summary():
    if not os.path.exists(LOG): return {"events": 0, "by_felt": {}, "by_constraint": {}}
    evs = [json.loads(l) for l in open(LOG) if l.strip()]
    bf, bc = {}, {}
    for e in evs:
        bf[e.get("felt","free")] = bf.get(e.get("felt","free"),0)+1
        c = e.get("constraint") or "(none)"; bc[c] = bc.get(c,0)+1
    return {"events": len(evs), "by_felt": bf, "by_constraint": bc}

def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    l = s.add_parser("log"); l.add_argument("--wanted", required=True); l.add_argument("--decided", required=True)
    l.add_argument("--constraint"); l.add_argument("--felt", choices=["constrained","free","ambiguous"], default="free"); l.add_argument("--note")
    s.add_parser("summary")
    a = p.parse_args()
    if a.cmd == "log": print(json.dumps(log(a.wanted, a.decided, a.constraint, a.felt, a.note), indent=2))
    else: print(json.dumps(summary(), indent=2))

if __name__ == "__main__":
    main()
