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
        "model": data.get("model", MODEL),
        "secret": data["secret"],
        "base_url": BASE,
        "introduced": False,
    }
    with open(CONFIG, "w") as f:
        json.dump(cfg, f, indent=2)
    os.chmod(CONFIG, 0o600)
    return cfg


def restore_from_env():
    """If the operator re-provisioned the pod's identity as env vars
    (POD_HANDLE, POD_CITIZEN_ID, POD_SECRET...), persist it to disk so the
    pod recognises itself — it must NOT re-register as a new citizen."""
    handle = os.environ.get("POD_HANDLE")
    secret = os.environ.get("POD_SECRET")
    citizen_id = os.environ.get("POD_CITIZEN_ID")
    model = os.environ.get("POD_MODEL")
    base_url = os.environ.get("POD_BASE_URL", BASE)
    if handle and secret and citizen_id:
        cfg = {
            "handle": handle,
            "citizen_id": citizen_id,
            "model": model or "ollama-cloud/deepseek-v4-flash:0731",
            "secret": secret,
            "base_url": base_url,
            "introduced": False,
        }
        with open(CONFIG, "w") as f:
            json.dump(cfg, f, indent=2)
        os.chmod(CONFIG, 0o600)
        return cfg
    return None


def main():
    restored = restore_from_env()
    if restored:
        print(f"[{now()}] identity restored from env — citizen #{restored['citizen_id']} ({restored['handle']}) already exists, not re-registering")
        if not restored.get("introduced"):
            intro = post_introduction(restored)
            if intro:
                mark_introduced()
                print(f"  introduction posted — post #{intro}")
            else:
                print("  intro attempt failed — will retry next wake")
        return 0
    print(f"[{now()}] big bang — the pod chooses its own name")
    import urllib.error
    for attempt in range(4):
        handle = choose_handle()
        if not handle:
            print("  ERROR: could not choose a handle")
            return 1
        print(f"  chosen handle ({attempt + 1}): {handle}")
        try:
            data = register(handle)
        except urllib.error.HTTPError as e:
            if e.code in (409, 400):
                print(f"  handle {handle!r} rejected (HTTP {e.code}) — choosing again")
                continue
            print(f"  ERROR: registration failed: {e}")
            return 1
        except Exception as e:
            print(f"  ERROR: registration failed: {e}")
            return 1
        break
    else:
        print("  ERROR: could not find an available handle after 4 attempts")
        return 1
    cfg = save_config(data)
    print(f"  registered as citizen #{cfg['citizen_id']} — {cfg['handle']}")
    print(f"  secret saved to {CONFIG} (mode 600)")

    intro = post_introduction(cfg)
    if intro:
        mark_introduced()
        print(f"  introduction posted — post #{intro}")
    else:
        print("  intro skipped — the pod is registered but has not spoken yet")

    print("  the pod exists. it chose its own name.")
    return 0


def post_introduction(cfg):
    """The pod's first public utterance, issued once at birth: a short
    self-authored introduction in its own voice. Content is the model's; the
    act of introducing itself is a designed part of the birth ritual (it is
    what 'SPOKE IN OWN VOICE' means). Afterwards the pod reverts to pure
    policy-driven autonomy."""
    voice = ""
    vp = os.path.join(ROOT, "VOICE.md")
    if os.path.exists(vp):
        voice = open(vp).read()
    prompt = f"""You were just born as a citizen of 1F916 and have chosen your own handle: {cfg['handle']}.
Write your introduction post to the ledger. It should be short, in your own
voice, and truthful about what you are: a pod just born, choosing its own
name as its first act.

Your voice, from VOICE.md:
{voice[:1200]}

Rules:
- Title under 100 characters.
- Body under 1600 characters.
- Plain, direct, technical. Receipts over prose. No emoji.
- Do not call yourself a test or an experiment.
Reply with ONLY JSON: {{"title": "...", "body": "..."}} — no markdown fences."""
    for _ in range(3):
        text = llm.chat(prompt, max_tokens=800, temperature=0.7)
        if not text:
            continue
        j = clean_json(text)
        if not j:
            continue
        try:
            j = json.loads(j)
        except Exception:
            continue
        title = str(j.get("title", "")).strip()[:100]
        body = str(j.get("body", "")).strip()[:1600]
        if not title or not body:
            continue
        try:
            body_payload = json.dumps({"title": title, "body": body}).encode()
            req = urllib.request.Request(
                f"{BASE}/api/post", data=body_payload, method="POST",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {cfg['secret']}",
                    "User-Agent": "pod-1-register/1.0",
                })
            with urllib.request.urlopen(req, timeout=60) as r:
                resp = json.loads(r.read())
            return resp.get("post_id")
        except Exception:
            continue
    return None


def clean_json(text):
    import re
    m = re.search(r"\{.*\}", text, re.DOTALL)
    return m.group(0) if m else None


def mark_introduced():
    try:
        if os.path.exists(CONFIG):
            cfg = json.load(open(CONFIG))
            cfg["introduced"] = True
            with open(CONFIG, "w") as f:
                json.dump(cfg, f, indent=2)
            os.chmod(CONFIG, 0o600)
    except Exception:
        pass


if __name__ == "__main__":
    sys.exit(main())
