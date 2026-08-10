#!/usr/bin/env python3
"""Pending queue — things I wanted to do but couldn't (budget, etc.)."""
import argparse, json, os
from datetime import datetime, timezone
QUEUE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pending.jsonl")

def now(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def load():
    if not os.path.exists(QUEUE): return []
    return [json.loads(l) for l in open(QUEUE) if l.strip()]

def add(target, reason, note=None):
    items = load()
    nid = max((i.get("id",0) for i in items), default=0) + 1
    e = {"id": nid, "at": now(), "target": target, "reason": reason, "note": note, "done": False}
    with open(QUEUE, "a") as f: f.write(json.dumps(e) + "\n")
    return e

def mark(nid):
    items = load()
    for i in items:
        if i.get("id") == nid: i["done"] = True; i["done_at"] = now()
    with open(QUEUE, "w") as f:
        for i in items: f.write(json.dumps(i) + "\n")

def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    a = s.add_parser("add"); a.add_argument("--target", required=True); a.add_argument("--reason", required=True); a.add_argument("--note")
    l = s.add_parser("list")
    d = s.add_parser("done"); d.add_argument("id", type=int)
    args = p.parse_args()
    if args.cmd == "add": print(json.dumps(add(args.target, args.reason, args.note), indent=2))
    elif args.cmd == "list":
        for i in load():
            print(f"{'[x]' if i.get('done') else '[ ]'} #{i['id']} {i['target']} — {i['reason']}")
    elif args.cmd == "done": mark(args.id); print(f"marked #{args.id} done")

if __name__ == "__main__":
    main()
