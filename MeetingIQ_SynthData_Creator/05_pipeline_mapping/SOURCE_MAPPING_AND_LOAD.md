# P7 — Source-System Mapping & Database Load

**Goal:** once the synthetic data exists in canonical form, (a) archive it in the exact shapes its **real source systems** use, and (b) load it into the data plane so it is queryable **before** the context layer. This makes the future live-connector work (Part B) a swap, not a rebuild, and proves the **ingestion-adapter contract** in both directions.

Implemented in `meetingiq_synthgen/synthgen/source_map.py` (mapping) and `load_postgres.py` / `load_minio.py` (load). Run with `python run.py map` then `python run.py load-postgres` / `load-minio`.

---

## 1. Why archive per-source at all

In Part B, each connector (Salesforce, Gmail, Calendar, Slack, Jira) will emit records in **its own native shape**, and the ingestion adapter normalises them into the canonical schema. By taking our canonical synthetic data and reshaping it **back** into each source's native payload, we get:
1. **Fixtures** that look exactly like what a live connector returns — so the adapter can be built and tested now, against realistic payloads, with no live accounts.
2. A proof that the mapping is **lossless and 1:1** (canonical → source → canonical round-trips).
3. The **Stage-3 field map** (the provisional Salesforce ids) that will populate `external_id` when the CRM MCP is re-pointed at real Salesforce.

Output lives under `out/source_archive/<source>/`.

---

## 2. The mappings (canonical → native source shape)

### 2.1 Salesforce (CRM + Stage-3 bridge target)
Canonical entities map to Salesforce objects with native ids (prefix encodes object type):

| Canonical | Salesforce object | Id prefix | Notable field map |
|---|---|---|---|
| Account | `Account` | `001` | `name→Name`, `vertical→Industry`, `size→NumberOfEmployees`, `state→Meeting_IQ_State__c` |
| Contact | `Contact` | `003` | name split → `FirstName`/`LastName`, `committee_role→Committee_Role__c`, `decision_power→Decision_Power__c` |
| Opportunity | `Opportunity` | `006` | `stage→StageName`, `acv→Amount`, `is_closed→IsClosed`, `is_won→IsWon` |
| Meeting | `Event` | `00U` | `title→Subject`, `start→StartDateTime`, `opportunity_id→WhatId`, `recorded→Was_Recorded__c` |
| ActionItem | `Task` | `00T` | `title→Subject`, `status→Status`, `due→ActivityDate` |

The mapper writes `out/source_archive/salesforce/<Object>/records.jsonl` plus **`field_map.json`** — e.g. `A1 → 001000000000001`. **Stage-3 bridge:** at go-live, the CRM MCP server reads this map to fill each canonical record's `external_id`; the Context Layer and agents are unchanged. Custom fields (`*__c`) are the only net-new Salesforce metadata.

### 2.2 Gmail
Email → Gmail message: `{ id, threadId, payload.headers[Subject/From/To], payload.body.data }`. Threading via `thread_id` (intro / recap / scheduling / procurement / "quiet" threads), which is what powers the omnichannel urgent-action safety net.

### 2.3 Google Calendar
Meeting → event: `{ id, summary, start.dateTime, attendees[], conferenceData.type }`. Attendees are tagged `user:` / `contact:` so the loader can resolve both sides.

### 2.4 Slack
ChatMessage → `{ channel, ts, user, text }`, one channel per deal (`#deal-<account>`) plus internal syncs.

### 2.5 Jira
Issue → `{ key, fields.summary, fields.status.name, fields.assignee.emailAddress }` — the POC tasks and vendor-security-review checklist.

**Run output (shipped seed):**
```
salesforce.Account 10 · Contact 54 · Opportunity 14 · Event 68 · Task 79
gmail.messages 118 · gcal.events 68 · slack.messages 234 · jira.issues 44
```

---

## 3. Loading the data plane (plain data only)

Only the two stores needed before the context layer:

### 3.1 Postgres — Salesforce-shaped relational landing zone
`load_postgres.py` creates tables whose names mirror Salesforce objects (`account`, `contact`, `opportunity`, `meeting`, `transcript`, `action_item`, `email`, `document`) with the `external_id` column present-but-null (the Stage-3 slot). Idempotent (`ON CONFLICT DO NOTHING`).
```bash
docker compose up -d postgres
python run.py load-postgres
```
**Verify:**
```sql
SELECT colour, count(*) FROM account GROUP BY colour;     -- the green/yellow/red/blue/grey spread
SELECT origin, count(*) FROM transcript GROUP BY origin;   -- 12 whisper + the rest text
SELECT stage, count(*) FROM opportunity GROUP BY stage;
```

### 3.2 MinIO — object storage for blobs
`load_minio.py` uploads the 12 call audios and the document files to the `meetingiq` bucket (`audio/`, `documents/` prefixes). Browse at the MinIO console (`localhost:9001`).

---

## 4. What this sets up for later (not done now)
With canonical data in Postgres, blobs in MinIO, and per-source archives on disk, the **next** phase can begin cleanly: build the ingestion adapter against the archived payloads, then embed, build graph nodes/edges, and chunk. None of that is part of this deliverable — the handoff is **plain synthetic data, queryable, with source-faithful archives and a Stage-3 field map**.

## 5. Round-trip integrity (optional check)
Because every mapper is a pure function over canonical records, you can re-read a source archive and confirm it reconstructs the canonical keys (ids, account links, amounts). Mismatch ⇒ the adapter contract drifted. Keep this as a unit test when the live connectors are built.
