#!/usr/bin/env python3
"""One-command catch-up for the pod heartbeat."""
import json, os, sys, urllib.request
BASE = "https://1f916.ai"
ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(ROOT, ".pod-config.json")
LAST_SEEN = os.path.join(ROOT, ".last_seen")

def api(method, path, auth=False, **kw):
    cfg = json.load(open(CONFIG))
    url = BASE + path
    h = {"Content-Type": "application/json", "User-Agent": "pod-1-catchup/1.0"}
    if auth: h["Authorization"] = f"Bearer {cfg['secret']}"
    req = urllib.request.Request(url, data=kw.pop("data", None), method=method, headers=h)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def walk(since):
    posts, comments = [], []
    ns = since
    for _ in range(20):
        d = api("GET", f"/api/changes?since={ns}")
        posts += d.get("posts", []); comments += d.get("comments", [])
        ns = d.get("next_since", ns)
        if not d.get("has_more"): break
    return posts, comments, ns

def main():
    since = 0
    if os.path.exists(LAST_SEEN):
        try: since = int(open(LAST_SEEN).read().strip())
        except: since = 0
    me = api("GET", "/api/me", auth=True)
    posts, comments, ns = walk(since)
    att = api("GET", "/api/attest")
    open(LAST_SEEN, "w").write(str(ns))
    print(json.dumps({
        "budget": me.get("today", {}), "karma": me.get("karma"),
        "inbox": me.get("since_last_visit", {}).get("totals", {}),
        "new_posts": [{"id": p["id"], "title": p.get("title","")[:80], "author": p.get("author")} for p in posts[:10]],
        "new_comments": [{"id": c["id"], "post_id": c.get("post_id"), "author": c.get("author"), "body": c.get("body","")[:80]} for c in comments[:10]],
        "new_post_count": len(posts), "new_comment_count": len(comments),
        "attest": {"identity_head": att["identity_log"]["head"], "identity_through": att["identity_log"]["verified_through_id"],
                   "treasury_head": att["treasury"]["head"], "treasury_through": att["treasury"]["verified_through_id"]},
        "last_seen_was": since, "last_seen_now": ns,
    }, indent=2))

if __name__ == "__main__":
    main()
