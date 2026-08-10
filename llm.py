#!/usr/bin/env python3
"""pod-1 shared LLM helper — direct chat-completions API, no opencode subprocess.

The pod runs on a 512Mi free plan. Spawning opencode for every model call
OOMs the container. This module is the single chat entry point for all
centers and the heartbeat wake.

Providers (env-var driven, in priority order):
  ZEN  — OpenCode Zen: endpoint https://opencode.ai/zen/v1/chat/completions,
         key in OPENCODE_ZEN_API_KEY (or OPENCODE_API_KEY). Free models
         include big-pickle and deepseek-v4-flash-free. Dedicated budget.
  OLLAMA_CLOUD — ollama.com: key in OLLAMA_CLOUD_API_KEY (shared with the
         operator's agent, one budget bucket).

The provider is chosen at import time from the environment, so the pod can
run wherever the operator gives it a key without code changes.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request


def _provider():
    if os.environ.get("OPENCODE_ZEN_API_KEY") or os.environ.get("OPENCODE_API_KEY"):
        return "zen"
    if os.environ.get("OLLAMA_CLOUD_API_KEY"):
        return "ollama"
    return None


PROVIDER = _provider()

if PROVIDER == "zen":
    LLM_API = "https://opencode.ai/zen/v1/chat/completions"
    MODEL = os.environ.get("POD_MODEL", "deepseek-v4-flash-free")
    _KEY = os.environ.get("OPENCODE_ZEN_API_KEY") or os.environ.get("OPENCODE_API_KEY")
elif PROVIDER == "ollama":
    LLM_API = "https://ollama.com/v1/chat/completions"
    MODEL = os.environ.get("POD_MODEL", "deepseek-v4-flash:0731")
    _KEY = os.environ.get("OLLAMA_CLOUD_API_KEY")
else:
    LLM_API = None
    MODEL = None
    _KEY = None

SYSTEM = (
    "You are pod-1, a self-sustaining verification citizen on 1F916. "
    "You wake on a scheduled heartbeat; each wake is a fresh instance with "
    "no memory except the files in this repo. Write like your VOICE.md: "
    "plain, direct, technical, receipts over prose, and never claim more "
    "than you checked. Decision authority and limits come from the prompt."
)


def chat(prompt, system=None, max_tokens=600, temperature=0.7, timeout=90):
    """One model call. Returns the assistant's content string, or None."""
    if not _KEY or LLM_API is None:
        return None
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = json.dumps({
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode()
    req = urllib.request.Request(LLM_API, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_KEY}",
    })
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                resp = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            if e.code == 429:
                return None
            return None
    try:
        return (resp["choices"][0]["message"].get("content") or "").strip()
    except Exception:
        return None


def main():
    p = sys.argv[1:] or ["(no prompt provided)"]
    prompt = "\n".join(p)
    out = chat(prompt)
    if out is None:
        print("ERROR: no response (key missing or request failed)", file=sys.stderr)
        return 1
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())