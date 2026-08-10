#!/usr/bin/env python3
"""Off-machine attest witness for pod-1."""
import argparse, hashlib, json, os, sys, time
from datetime import datetime, timezone
import requests
BASE = "https://1f916.ai"
DEFAULT_LOG = os.path.join(os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share")), "1f916", "attest_log.jsonl")

def fetch():
    r = requests.get(f"{BASE}/api/attest", timeout=30); r.raise_for_status()
    return r.json(), r.text

def digest(raw): return hashlib.sha256(raw.encode()).hexdigest()

def build(data, raw):
    return {"recorded_at_ms": int(time.time()*1000),
            "recorded_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "response_sha256": digest(raw),
            "identity": {"head": data["identity_log"]["head"], "verified_through_id": data["identity_log"]["verified_through_id"], "status": data["identity_log"]["status"]},
            "treasury": {"head": data["treasury"]["head"], "verified_through_id": data["treasury"]["verified_through_id"], "status": data["treasury"]["status"]},
            "endpoint": f"{BASE}/api/attest"}

def load(path):
    rows = []
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                try: rows.append(json.loads(line))
                except: pass
    return rows

def record(path, on_change=False):
    data, raw = fetch()
    e = build(data, raw)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if on_change:
        rows = load(path)
        if rows:
            last = rows[-1]
            if last["identity"]["head"] == e["identity"]["head"] and last["treasury"]["head"] == e["treasury"]["head"]:
                return None
    with open(path, "a") as f: f.write(json.dumps(e) + "\n")
    return e

def verify(path, index):
    rows = load(path)
    if not rows: sys.exit("no witness entries")
    e = rows[index if index is not None else -1]
    ident = e["identity"]
    r = requests.get(f"{BASE}/api/attest", params={"identity_from": ident["verified_through_id"], "identity_expect": ident["head"]}, timeout=30)
    r.raise_for_status(); d = r.json()["identity_log"]
    return {"expected_head": ident["head"], "status": d["status"], "expect_matches": d.get("expect_matches"), "head_now": d["head"]}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--log", default=DEFAULT_LOG)
    p.add_argument("--record", action="store_true")
    p.add_argument("--record-on-change", action="store_true")
    p.add_argument("--verify", nargs="?", const=-1, type=int)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    if a.record or a.record_on_change:
        e = record(a.log, on_change=a.record_on_change)
        if a.json: print(json.dumps(e if e else {"changed": False}, indent=2))
        elif e: print(f"recorded {e['recorded_at_utc']} identity {e['identity']['head'][:16]} treasury {e['treasury']['head'][:16]}")
        else: print("unchanged")
    elif a.verify is not None:
        r = verify(a.log, a.verify)
        print(json.dumps(r, indent=2) if a.json else f"expect_matches: {r['expect_matches']} status: {r['status']}")

if __name__ == "__main__":
    main()
