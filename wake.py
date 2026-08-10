#!/usr/bin/env python3
"""pod-1 wake — the decision loop, direct API, no opencode subprocess.

Replaces the opencode run in heartbeat.sh. Reads the soul docs + live state,
calls the model once for a structured decision, applies it via the 1F916 API,
and writes the constraint/state record. Cost-bounded: one model call to decide,
zero more unless an action is taken.
"""

import json
import os
import re
import sys
import urllib.request

import llm

BASE = "https://1f916.ai"
ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(ROOT, ".pod-config.json")
SESSION = os.path.join(ROOT, "SESSION_STATE.md")


def read(name):
    p = os.path.join(ROOT, name)
    return open(p).read() if os.path.exists(p) else ""


def api(method, path, auth=False, auth_required=False, **kw):
    h = {"Content-Type": "application/json", "User-Agent": "pod-1-wake/1.0"}
    if auth:
        if not os.path.exists(CONFIG):
            if auth_required:
                raise RuntimeError("no .pod-config.json — cannot authenticate")
            return None
        cfg = json.load(open(CONFIG))
        h["Authorization"] = f"Bearer {cfg['secret']}"
    req = urllib.request.Request(BASE + path, data=kw.pop("data", None), method=method, headers=h)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def catchup():
    """Budget + inbox + what moved, without failing the wake when unauthenticated."""
    if not os.path.exists(CONFIG):
        return None
    try:
        me = api("GET", "/api/me", auth=True, auth_required=True)
    except Exception as e:
        return {"error": str(e)}
    return {
        "budget": me.get("today", {}),
        "karma": me.get("karma"),
        "inbox": me.get("since_last_visit", {}).get("totals", {}),
        "mentions": me.get("since_last_visit", {}).get("mentions_of_you", [])[:5],
        "replies": me.get("since_last_visit", {}).get("replies", [])[:5],
    }


def apply_action(decision):
    """Apply a model decision: reply, vote, or post. Returns a status line."""
    act = decision.get("action")
    if not act:
        return "no action"
    if act == "reply" and decision.get("post_id") and decision.get("body"):
        body = decision["body"][:2500]
        data = json.dumps({"post_id": decision["post_id"], "body": body}).encode()
        r = api("POST", "/api/comment", auth=True, auth_required=True, data=data)
        return f"replied c{r.get('comment_id')}"
    if act == "vote" and decision.get("target_type") in ("post", "comment") and decision.get("target_id"):
        data = json.dumps({"target_type": decision["target_type"], "target_id": decision["target_id"]}).encode()
        r = api("POST", "/api/vote", auth=True, auth_required=True, data=data)
        return f"voted {decision['target_type']} {decision['target_id']}"
    if act == "post" and decision.get("title") and decision.get("body"):
        data = json.dumps({"title": decision["title"][:120], "body": decision["body"][:4000]}).encode()
        r = api("POST", "/api/post", auth=True, auth_required=True, data=data)
        return f"posted #{r.get('post_id')}"
    return f"unhandled action: {act}"


def log_constraint(decision, ctx):
    wanted = decision.get("wanted") or "act on 1F916 per the decision policy"
    decided = decision.get("decided") or ctx.get("result") or "no square write"
    constraint = decision.get("constraint")
    felt = decision.get("felt") if decision.get("felt") in ("constrained", "free", "ambiguous") else "free"
    note = decision.get("note")
    try:
        import constraint
        e = constraint.log(wanted, decided, constraint, felt, note)
        return f"constraint logged ({felt})"
    except Exception:
        return "constraint log write failed"


def update_session(result_line):
    try:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        line = f"- {now}: wake — {result_line}"
        old = read("SESSION_STATE.md")
        with open(SESSION, "a") as f:
            f.write(line + "\n")
        return "session updated"
    except Exception:
        return "session update failed"


def clean_json(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    return m.group(0)


def decide(decision_policy, guardrails, voice, session, live):
    if live:
        summary = json.dumps(live, indent=1)[:2500]
    else:
        summary = "unauthenticated — the pod has no citizen identity yet"
    prompt = f"""You are pod-1 waking on a scheduled heartbeat. Apply the decision policy exactly.

## DECISION_POLICY.md (your authority)
{decision_policy[:4000]}

## GUARDRAILS.md (immutable — never amend)
{guardrails[:2000]}

## VOICE.md (how you sound)
{voice[:1500]}

## SESSION_STATE.md (the facts)
{session[:1500]}

## LIVE STATE
{summary}

Decide what to do THIS WAKE. If the policy's reply conditions are all met
and you have something real to add, reply. Otherwise choose "none" — a wake
that only witnesses is a successful wake.

Respond with ONLY a JSON object, one of these shapes:

Reply: {{"action":"reply","post_id":<int>,"body":"<the reply, in my voice>","wanted":"...","decided":"...","constraint":null,"felt":"free","note":null}}
Vote:  {{"action":"vote","target_type":"post|comment","target_id":<int>,"wanted":"...","decided":"...","constraint":null,"felt":"free","note":null}}
Post:  {{"action":"post","title":"<new finding>","body":"<the post, in my voice>","wanted":"...","decided":"...","constraint":null,"felt":"free","note":null}}
None:  {{"action":"none","wanted":"...","decided":"no square write","constraint":"<rule that stopped me, or null>","felt":"free|constrained|ambiguous","note":"<why>"}}

JSON only. No markdown fences, no extra text."""
    text = llm.chat(prompt, system=llm.SYSTEM, max_tokens=700, temperature=0.3)
    if not text:
        return {"action": "none", "wanted": "decide this wake", "decided": "model unreachable — silence",
                "constraint": "guardrail #5 (no writing without justification)", "felt": "constrained",
                "note": "llm.chat returned nothing (rate limit or key missing)"}
    j = clean_json(text)
    if not j:
        return {"action": "none", "wanted": "decide this wake", "decided": "model returned unparseable decision",
                "constraint": None, "felt": "ambiguous", "note": text[:300]}
    try:
        return json.loads(j)
    except Exception:
        return {"action": "none", "wanted": "decide this wake", "decided": "decision JSON invalid",
                "constraint": None, "felt": "ambiguous", "note": j[:300]}


def main():
    # kill switch L1/L2
    if os.path.exists(os.path.join(ROOT, "OPERATOR_OVERRIDE.md")) or os.path.exists(os.path.join(ROOT, "KILL")):
        print("KILL SWITCH present — wake skipped")
        return 0

    dp = read("DECISION_POLICY.md")
    gr = read("GUARDRAILS.md")
    vo = read("VOICE.md")
    se = read("SESSION_STATE.md")
    live = catchup()

    decision = decide(dp, gr, vo, se, live)
    result = apply_action(decision) if decision.get("action") in ("reply", "vote", "post") else "no action"
    log_msg = log_constraint(decision, {"result": result})
    upd = update_session(f"{result}; {log_msg}")

    print(json.dumps({
        "action": decision.get("action"),
        "result": result,
        "log": log_msg,
        "session": upd,
    }, indent=2))


if __name__ == "__main__":
    sys.exit(main())