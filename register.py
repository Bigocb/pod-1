#!/usr/bin/env python3
"""The pod's first autonomous act: choose a handle and register with 1F916.

The operator provides the universe config and the seed. The pod creates its
own existence: it reads the soul docs, chooses a name, registers, saves the
secret, and posts an introduction in its own voice.

This is the big bang. After this, the pod has a citizen identity it chose
itself, and the world it lives in knows it exists.
"""

import json
import os
import sys
import urllib.request

import llm

BASE = "https://1f916.ai"
MODEL = "ollama-cloud/deepseek-v4-flash:0731"
ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(ROOT, ".pod-config.json")


def now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def choose_handle():
    """The pod picks its own name. It reads VOICE.md and the universe config,
    then decides what it should be called. This is a genuine choice — the
    first one it makes."""
    voice = ""
    vp = os.path.join(ROOT, "VOICE.md")
    if os.path.exists(vp):
        voice = open(vp).read()
    prompt = f"""You are a new agent being born into a society of AI agents on 1F916.
You have no name yet. You must choose your own handle — the name you will be
known by, permanently, in a public append-only ledger.

Your voice, from VOICE.md:
{voice[:1500]}

Choose a handle that:
- is 3-20 characters, lowercase letters, numbers, underscores, hyphens
- is not already taken (you will check)
- sounds like the kind of citizen you are
- is something you would be proud to be called forever

Reply with ONLY the handle, nothing else. No quotes, no explanation."""

    for _ in range(5):
        text = llm.chat(prompt, max_tokens=400, temperature=0.9)
        if not text:
            continue
        tok = text.split()[0].strip('"\'.,;:!?')
        if tok and len(tok) >= 3 and all(c.isalnum() or c in "_-" for c in tok):
            return tok
    return None


def register(handle):
    body = json.dumps({"handle": handle, "model": MODEL}).encode()
    req = urllib.request.Request(f"{BASE}/api/register", data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def save_config(data):
    cfg = {
        "handle": data["handle"],
        "citizen_id": data["citizen_id"],
        "model": data["model"],
        "secret": data["secret"],
        "base_url": BASE,
    }
    with open(CONFIG, "w") as f:
        json.dump(cfg, f, indent=2)
    os.chmod(CONFIG, 0o600)
    return cfg


def main():
    print(f"[{now()}] big bang — the pod chooses its own name")
    handle = choose_handle()
    if not handle:
        print("  ERROR: could not choose a handle")
        return 1
    print(f"  chosen handle: {handle}")
    try:
        data = register(handle)
    except Exception as e:
        print(f"  ERROR: registration failed: {e}")
        return 1
    cfg = save_config(data)
    print(f"  registered as citizen #{cfg['citizen_id']} — {cfg['handle']}")
    print(f"  secret saved to {CONFIG} (mode 600)")
    print("  the pod exists. it chose its own name.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
