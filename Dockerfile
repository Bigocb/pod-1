# pod-1 — the self-sustaining agent pod
# The operator runs `docker compose up` — the big bang — and walks away.
# The pod bootstraps itself, runs its centers, and manages its own life.

FROM python:3.12-slim

# deps for httpx-free python + curl for rollout checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git cron ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /pod

# copy the universe
COPY . .

# python deps
RUN pip install --no-cache-dir requests

# the entrypoint: bootstrap, start cron, keep alive
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh /pod/heartbeat.sh /pod/centers/daily.sh /pod/centers/run_center.sh /pod/centers/weekly.sh

# state volume — memory survives container restarts
VOLUME ["/pod/state"]

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
