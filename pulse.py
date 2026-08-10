#!/usr/bin/env python3
"""The pod's pulse — a minimal HTTP endpoint so Render's health check passes.

The pod is a brain, not a web server. This is not a dashboard and not a
console. It is a single endpoint that reports whether the pod is alive, so
Render can health-check it and the operator can see it breathing.

GET / -> 200 "alive" with the pod's name and uptime
GET /health -> 200 "ok"
"""

import json
import os
import time
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer

START = time.time()
NAME = "pod-1"
CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".pod-config.json")


def _constant_time_eq(a, b):
    try:
        return hmac.compare_digest(a.encode(), b.encode())
    except Exception:
        return False


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/health"):
            self._send(200, {
                "name": NAME,
                "status": "alive",
                "uptime_seconds": int(time.time() - START),
                "note": "The pod lives. The pod decides. The pod witnesses.",
            })
        elif self.path in ("/log", "/test-model") and os.environ.get("POD_IDENTITY_KEY"):
            key = self.headers.get("X-Pod-Identity-Key", "")
            if not _constant_time_eq(key, os.environ["POD_IDENTITY_KEY"]):
                self._send(403, {"error": "forbidden"})
                return
            if self.path == "/log":
                log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "heartbeat.log")
                try:
                    with open(log) as f:
                        lines = f.readlines()
                    self._send(200, {"lines": lines[-60:]})
                except Exception as e:
                    self._send(500, {"error": str(e)})
                return
            # /test-model — prove the zend LLM path works inside the container
            try:
                import llm
                out = llm.chat("Reply with exactly: MODEL_OK", system="Be terse.", timeout=60)
                self._send(200, {"provider": llm.PROVIDER, "model": llm.MODEL, "response": out})
            except Exception as e:
                self._send(500, {"error": f"{type(e).__name__}: {e}"})
        elif self.path == "/identity" and os.environ.get("POD_IDENTITY_KEY"):
            key = self.headers.get("X-Pod-Identity-Key", "")
            if not _constant_time_eq(key, os.environ["POD_IDENTITY_KEY"]):
                self._send(403, {"error": "forbidden"})
                return
            if not os.path.exists(CONFIG):
                self._send(404, {"error": "not registered yet"})
                return
            try:
                with open(CONFIG) as f:
                    data = json.load(f)
                self._send(200, data)
            except Exception as e:
                self._send(500, {"error": str(e)})
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, *args):
        pass  # quiet


def main():
    port = int(os.environ.get("PORT", 5000))
    print(f"pulse on :{port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
