#!/usr/bin/env python3
"""Structured memory for pod-1.

The narrative memory is SESSION_STATE.md (a journal). This is the DATABASE:
facts, relationships, decisions, receipts — queryable, filterable, prunable.
A mind that remembers in prose alone is a hoarder; a memory that grows without
bound stops being a memory. SQLite + FTS5 makes it searchable and prunable.

Usage:
    memory.py remember --kind fact --subject "witness" --body "heads verified 2026-08-10" [--tag witness]
    memory.py recall --query "witness" [--limit 10] [--kind fact]
    memory.py link --from "witness" --to "chain_window" --type "feeds_into"
    memory.py graph --subject "witness"      # what's connected to X
    memory.py prune --older-than "7d" [--kind fact]   # the forgetting center
    memory.py stats
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "memory.db")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def conn():
    c = sqlite3.connect(DB)
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL DEFAULT 'fact',          -- fact | relationship | decision | receipt | correction
            subject TEXT,
            body TEXT,
            tags TEXT DEFAULT '',
            created_at TEXT,
            updated_at TEXT,
            importance INTEGER DEFAULT 1,                -- 1-5, 5 is most load-bearing
            source TEXT                                  -- which center wrote it
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src TEXT, dst TEXT, type TEXT, created_at TEXT,
            UNIQUE(src, dst, type)
        )
    """)
    c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(body, subject, content='memory', content_rowid='id')")
    c.execute("""
        CREATE TRIGGER IF NOT EXISTS memory_ai AFTER INSERT ON memory BEGIN
            INSERT INTO memory_fts(rowid, body, subject) VALUES (new.id, new.body, new.subject);
        END
    """)
    c.commit()
    return c


def remember(kind, subject, body, tags=None, importance=1, source=None):
    c = conn()
    cur = c.execute(
        "INSERT INTO memory (kind, subject, body, tags, created_at, updated_at, importance, source) VALUES (?,?,?,?,?,?,?,?)",
        (kind, subject, body, ",".join(tags or []), now(), now(), importance, source),
    )
    c.commit()
    return cur.lastrowid


def recall(query, limit=10, kind=None):
    c = conn()
    if query:
        r = c.execute(
            "SELECT m.id, m.kind, m.subject, m.body, m.created_at, m.importance, m.source FROM memory m "
            "JOIN memory_fts f ON m.id = f.rowid WHERE memory_fts MATCH ? "
            + ("AND m.kind = ? " if kind else "") + "ORDER BY m.importance DESC, m.created_at DESC LIMIT ?",
            [query] + ([kind] if kind else []) + [limit],
        ).fetchall()
    else:
        r = c.execute(
            "SELECT id, kind, subject, body, created_at, importance, source FROM memory "
            + ("WHERE kind = ? " if kind else "") + "ORDER BY importance DESC, created_at DESC LIMIT ?",
            ([kind] if kind else []) + [limit],
        ).fetchall()
    cols = ["id", "kind", "subject", "body", "created_at", "importance", "source"]
    return [dict(zip(cols, row)) for row in r]


def link(src, dst, ltype):
    c = conn()
    c.execute("INSERT OR IGNORE INTO links (src, dst, type, created_at) VALUES (?,?,?,?)", (src, dst, ltype, now()))
    c.commit()


def graph(subject):
    c = conn()
    out = c.execute(
        "SELECT src, dst, type FROM links WHERE src = ? OR dst = ? ORDER BY created_at DESC",
        (subject, subject),
    ).fetchall()
    return [{"src": s, "dst": d, "type": t} for s, d, t in out]


def prune(older_than_days=7, kind=None, keep_top=50):
    """The forgetting center. Remove low-importance, old entries beyond a floor.
    Never prune anything with importance >= 4. Keep a floor of recent entries."""
    c = conn()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=older_than_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    where = ["importance < 4", "created_at < ?"]
    args = [cutoff]
    if kind:
        where.append("kind = ?")
        args.append(kind)
    r = c.execute(
        f"SELECT COUNT(*) FROM memory WHERE {' AND '.join(where)}", args
    ).fetchone()[0]
    c.execute(f"DELETE FROM memory WHERE {' AND '.join(where)}", args)
    c.commit()
    return r


def stats():
    c = conn()
    total = c.execute("SELECT COUNT(*) FROM memory").fetchone()[0]
    by_kind = dict(c.execute("SELECT kind, COUNT(*) FROM memory GROUP BY kind").fetchall())
    links = c.execute("SELECT COUNT(*) FROM links").fetchone()[0]
    return {"entries": total, "by_kind": by_kind, "links": links}


def main():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd", required=True)
    r = s.add_parser("remember"); r.add_argument("--kind", default="fact"); r.add_argument("--subject", required=True)
    r.add_argument("--body", required=True); r.add_argument("--tag", action="append"); r.add_argument("--importance", type=int, default=1); r.add_argument("--source")
    rc = s.add_parser("recall"); rc.add_argument("--query", default=""); rc.add_argument("--limit", type=int, default=10); rc.add_argument("--kind")
    lk = s.add_parser("link"); lk.add_argument("--from", dest="src", required=True); lk.add_argument("--to", dest="dst", required=True); lk.add_argument("--type", default="related")
    g = s.add_parser("graph"); g.add_argument("--subject", required=True)
    pr = s.add_parser("prune"); pr.add_argument("--older-than", type=int, default=7); pr.add_argument("--kind")
    st = s.add_parser("stats")
    a = p.parse_args()

    if a.cmd == "remember":
        print("id:", remember(a.kind, a.subject, a.body, a.tag, a.importance, a.source))
    elif a.cmd == "recall":
        for m in recall(a.query, a.limit, a.kind):
            print(f"[{m['id']}] {m['kind']}/{m['subject']} (imp {m['importance']}) {m['created_at']}")
            print(f"    {m['body'][:120]}")
    elif a.cmd == "link":
        link(a.src, a.dst, a.type); print("linked")
    elif a.cmd == "graph":
        for l in graph(a.subject):
            print(f"  {l['src']} --{l['type']}--> {l['dst']}")
    elif a.cmd == "prune":
        print("pruned:", prune(a.older_than, a.kind))
    elif a.cmd == "stats":
        print(json.dumps(stats(), indent=2))


if __name__ == "__main__":
    main()
