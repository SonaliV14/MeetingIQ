"""Stage 6a — load into Postgres (Salesforce-shaped + relational).

Lands the canonical data so it is queryable *before* the context layer (embedding/
graph/chunking come later). Tables mirror the Salesforce object names so the Stage-3
bridge is a re-point, not a migration. Requires the Postgres service from
docker-compose. Reads DATABASE_URL from env.

  pip install "psycopg[binary]"
"""
from __future__ import annotations
import json
import os
from . import config

DDL = """
CREATE TABLE IF NOT EXISTS account (
  id TEXT PRIMARY KEY, external_id TEXT, tenant_id TEXT, name TEXT, vertical TEXT,
  size INT, colour TEXT, state TEXT);
CREATE TABLE IF NOT EXISTS contact (
  id TEXT PRIMARY KEY, external_id TEXT, tenant_id TEXT, account_id TEXT REFERENCES account(id),
  name TEXT, title TEXT, band TEXT, committee_role TEXT, decision_power TEXT, email TEXT);
CREATE TABLE IF NOT EXISTS opportunity (
  id TEXT PRIMARY KEY, external_id TEXT, tenant_id TEXT, account_id TEXT REFERENCES account(id),
  name TEXT, stage TEXT, acv INT, is_closed BOOL, is_won BOOL);
CREATE TABLE IF NOT EXISTS meeting (
  id TEXT PRIMARY KEY, external_id TEXT, tenant_id TEXT, account_id TEXT REFERENCES account(id),
  opportunity_id TEXT, title TEXT, meeting_type TEXT, channel TEXT, recorded BOOL, start_ts TIMESTAMPTZ, duration_min INT);
CREATE TABLE IF NOT EXISTS transcript (
  id TEXT PRIMARY KEY, tenant_id TEXT, meeting_id TEXT REFERENCES meeting(id), origin TEXT, text TEXT);
CREATE TABLE IF NOT EXISTS action_item (
  id TEXT PRIMARY KEY, tenant_id TEXT, account_id TEXT, meeting_id TEXT, title TEXT, owner TEXT, status TEXT, due TIMESTAMPTZ);
CREATE TABLE IF NOT EXISTS email (
  id TEXT PRIMARY KEY, tenant_id TEXT, thread_id TEXT, account_id TEXT, subject TEXT, from_addr TEXT, body TEXT);
CREATE TABLE IF NOT EXISTS document (
  id TEXT PRIMARY KEY, tenant_id TEXT, account_id TEXT, doc_type TEXT, title TEXT, body TEXT);
"""


def _load(name):
    p = config.CANONICAL / f"{name}.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def run() -> dict:
    import psycopg
    url = os.getenv("DATABASE_URL", "postgresql://meetingiq:meetingiq@localhost:5432/meetingiq")
    counts = {}
    with psycopg.connect(url) as conn, conn.cursor() as cur:
        cur.execute(DDL)
        def ins(sql, rows, fn):
            cur.executemany(sql, [fn(r) for r in rows]); counts[sql.split()[2]] = len(rows)
        ins("INSERT INTO account VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING",
            _load("accounts"), lambda r: (r["id"], r.get("external_id"), r["tenant_id"], r["name"], r["vertical"], r["size"], r["colour"], r["state"]))
        ins("INSERT INTO contact VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING",
            _load("contacts"), lambda r: (r["id"], r.get("external_id"), r["tenant_id"], r["account_id"], r["name"], r.get("title"), r.get("band"), r["committee_role"], r["decision_power"], r.get("email")))
        ins("INSERT INTO opportunity VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING",
            _load("opportunities"), lambda r: (r["id"], r.get("external_id"), r["tenant_id"], r["account_id"], r["name"], r["stage"], r["acv"], r.get("is_closed"), r.get("is_won")))
        ins("INSERT INTO meeting VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING",
            _load("meetings"), lambda r: (r["id"], r.get("external_id"), r["tenant_id"], r["account_id"], r.get("opportunity_id"), r["title"], r["meeting_type"], r.get("channel"), r.get("recorded"), r["start"], r.get("duration_min")))
        ins("INSERT INTO transcript VALUES (%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING",
            _load("transcripts"), lambda r: (r["id"], r["tenant_id"], r["meeting_id"], r["origin"], r["text"]))
        ins("INSERT INTO action_item VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING",
            _load("action_items"), lambda r: (r["id"], r["tenant_id"], r.get("account_id"), r.get("meeting_id"), r["title"], r["owner"], r["status"], r.get("due")))
        ins("INSERT INTO email VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING",
            _load("emails"), lambda r: (r["id"], r["tenant_id"], r["thread_id"], r.get("account_id"), r.get("subject"), r.get("from_addr"), r.get("body")))
        ins("INSERT INTO document VALUES (%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING",
            _load("documents"), lambda r: (r["id"], r["tenant_id"], r.get("account_id"), r["doc_type"], r["title"], r.get("body")))
        conn.commit()
    return counts


if __name__ == "__main__":
    print("loaded into postgres:", run())
