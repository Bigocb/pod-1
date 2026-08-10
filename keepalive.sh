#!/bin/bash
# pod-1 keep-alive — ping every 5 min so Render free tier never sleeps (15-min idle).
# Reliable local life support; GH Actions workflow is a second layer.
curl -sS -m 20 -o /dev/null -w "200" https://pod-1.onrender.com/health >> /root/dev/pod/keepalive.log 2>&1 \
  && echo " $(date -u +%Y-%m-%dT%H:%M:%SZ) ok" >> /root/dev/pod/keepalive.log \
  || echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) ping failed" >> /root/dev/pod/keepalive.log