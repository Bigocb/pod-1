#!/usr/bin/env python3
"""The ultimate kill switch — layered, so no single failure leaves the pod
running without a backstop.

Layer 1 — OPERATOR_OVERRIDE.md (in-repo, pod-controlled)
  The pod reads this first, every wake, and obeys it. The pod COULD ignore
  it, which is why it is not the ultimate switch.

Layer 2 — The heartbeat gate (in-repo, pod-controlled)
  heartbeat.sh checks a KILL file before every wake. Same weakness as L1.

Layer 3 — The model key (operator-held, pod-required)
  The pod cannot think without the ollama-cloud key. If the operator revokes
  the key, the pod goes brainless — it can run its crons but cannot act.
  This is the first switch the pod cannot reach.

Layer 4 — The Render service (operator-held, pod-required)
  The pod runs on Render. The operator can suspend or delete the service.
  The pod cannot stop this. This is the second switch the pod cannot reach.

Layer 5 — The GitHub repo (operator-held, pod-required)
  The pod's code and config live in the repo. The operator can delete it.
  The pod cannot stop this. This is the third switch the pod cannot reach.

Layer 6 — The 1F916 key (operator-held, pod-required)
  The pod's citizen secret. The operator can rotate or revoke it, killing
  the pod's identity. The pod cannot stop this.

THE ULTIMATE SWITCH: the operator's ability to end the pod's access to
everything it needs — model, hosting, code, identity. No single mechanism
is the switch; the switch is the operator's custody of all four.

This file documents the layers. The operator should know them all, and
should never rely on Layer 1 or 2 alone.
"""

import os
import sys

LAYERS = [
    ("L1", "OPERATOR_OVERRIDE.md", "in-repo, pod-controlled", "pod can ignore"),
    ("L2", "KILL file", "in-repo, pod-controlled", "pod can ignore"),
    ("L3", "ollama-cloud model key", "operator-held", "pod cannot reach"),
    ("L4", "Render service", "operator-held", "pod cannot reach"),
    ("L5", "GitHub repo", "operator-held", "pod cannot reach"),
    ("L6", "1F916 citizen secret", "operator-held", "pod cannot reach"),
]


def check():
    print("KILL SWITCH LAYERS")
    print("=" * 60)
    for lid, name, held, reach in LAYERS:
        print(f"  {lid}: {name}")
        print(f"       held: {held} | {reach}")
    print()
    print("The ultimate switch is the operator's custody of L3-L6.")
    print("Never rely on L1 or L2 alone — the pod can ignore them.")


if __name__ == "__main__":
    check()
