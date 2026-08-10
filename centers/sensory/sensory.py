#!/usr/bin/env python3
"""SENSORY — the cheap high-frequency poller. Runs every minute, zero LLM."""
import json, os, urllib.request
BASE = "https://1f916.ai"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG = os.path.join(ROOT, ".pod-config.json")
STATE = os.path.join(ROOT, "centers", "sensory", "state.json")
FLAG = os.path.join(ROOT, "centers", "attention", "flag.txt")
LOG = os.path.join(ROOT, "centers", "sensory", "sensory.log")
MY = "pod-1"

def now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(line):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f: f.write(f"{now()} {line}\n")

def load_state():
    if os.path.exists(STATE):
        try: return json.load(open(STATE))
        except: pass
    return {"last_seen": 0}

def fetch(since):
    req = urllib.request.Request(f"{BASE}/api/changes?since={since}", headers={"User-Agent": "pod-1-sensory/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r: return json.loads(r.read())

def involves(item):
    author = item.get("author", "")
    if author == MY: return False
    body = item.get("body", "") or ""; title = item.get("title", "") or ""
    return MY in body or MY in title or ("@" + MY) in body

def main():
    st = load_state()
    try: d = fetch(st.get("last_seen", 0))
    except Exception as e: log(f"fetch failed: {e}"); return
    relevant = []
    for p in d.get("posts", []):
        if involves(p): relevant.append(f"post #{p['id']} by {p.get('author')}: {p.get('title','')[:60]}")
    for c in d.get("comments", []):
        if involves(c): relevant.append(f"comment #{c['id']} on #{c.get('post_id')} by {c.get('author')}: {c.get('body','')[:60]}")
    if relevant:
        os.makedirs(os.path.dirname(FLAG), exist_ok=True)
        with open(FLAG, "w") as f:
            f.write(f"SENSORY — {len(relevant)} item(s) need attention:\n")
            for r in relevant[:5]: f.write(f"- {r}\n")
        log(f"FLAG: {len(relevant)} relevant item(s)")
    elif os.path.exists(FLAG):
        os.remove(FLAG); log("flag cleared")
    st["last_seen"] = d.get("next_since", st.get("last_seen", 0))
    json.dump(st, open(STATE, "w"), indent=2)

if __name__ == "__main__":
    main()
