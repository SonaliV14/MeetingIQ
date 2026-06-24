# P6 — Synthetic Data Build (Step-by-Step)

**Goal:** turn the Rapid7 scenario (`../03_client_scenario/SCENARIO_RAPID7.md`) into plain, source-shaped, validated data plus a hidden ground-truth ledger — **stopping before** embeddings/graph/chunking. Everything here is implemented in the bundled package `meetingiq_synthgen/`; this doc is the runbook with **what to expect at each step**.

**Environment:** see `ENV_AND_REQUIREMENTS.md`. **Run from:** `meetingiq_synthgen/`.

**Design rules honoured by the build:**
- Deterministic skeleton (Polars + Faker, fixed `SEED`) → reproducible structure.
- LLM expands each row into rich artifacts and **weaves in the planted signals**.
- The **ground-truth ledger is written as signals are planted** — never reverse-engineered.
- Validation gates every run (referential integrity, target bounds, ledger coverage, JSON-schema).
- Only Postgres + MinIO are touched; the context-layer stores stay off.

---

## Stage 0 — environment check (offline)
```bash
uv pip install -r requirements.txt
python run.py skeleton && python run.py validate
```
**Expect:** a counts block and `RESULT: PASS`. If this works, the rest is incremental.

---

## Stage 1 — deterministic skeleton (offline, Polars + Faker)
```bash
python run.py skeleton
```
**What it does:** builds the *structure* — users, the 10 accounts, firmographics, buying-committee contacts (hero committees hand-authored, others role-templated), opportunities, the meeting series (dates as offsets from `DEMO_TODAY`, with exactly **12** flagged for audio), action items, and **stubs** for emails/Slack/Jira/docs/news (bodies empty). It also seeds the **ground-truth ledger** with each deal's planted-signal plan, BANT/MEDDICC truth, and win/loss.

**Output:** `out/skeleton/*.jsonl` (+ parquet for accounts/contacts/opportunities/meetings) and `out/ground_truth_ledger.json`.

**Expect (with the shipped seed):**
```
users 7 · accounts 10 · firmographics 10 · contacts 54 · opportunities 14
meetings 68 · action_items 79 · emails 118 · slack 234 · jira 44
documents 30 · news 23 · audio_meetings 12 · ledger_deals 10
```
**Verify the world is right:** hero meetings for A1 (Meridian) span Jan→Jun with the last in the future; A5 (Vantage) trajectory is `declining`; A8 (Helios) carries `win_loss: lost`. Re-running produces identical files (determinism).

---

## Stage 2 — LLM expansion (needs `ANTHROPIC_API_KEY`)
```bash
python run.py expand
```
**What it does:** for each non-internal meeting, calls Claude to write a realistic transcript that **naturally embeds that meeting's planted signals** (read from the ledger); writes recap/scheduling/intro/procurement email bodies; writes documents (proposal, battlecard, POC criteria). Idempotent — re-runs skip files that exist.

**Output:** `out/artifacts/transcript_*.txt`, `email_*.txt`, `doc_*.md`.

**Expect:** ~53 transcripts, ~118 emails, ~30 docs (a few minutes on Sonnet; cost ≈ a dollar). Spot-check a Vantage transcript — it should contain a budget-freeze line and a Tenable mention without ever labelling them as "signals".

---

## Stage 3 — TTS for the 12 calls (needs a TTS provider; or offline pyttsx3)
```bash
python run.py tts        # provider via SYNTHGEN_TTS in .env
```
**What it does:** for the 12 audio-flagged meetings only, splits the transcript into `Name: line` turns, assigns a distinct voice per speaker, synthesises each turn, and concatenates to one file per meeting. (ffmpeg must be on PATH for concat.)

**Output:** `out/audio/<meeting_id>.mp3` ×12.

**Expect:** 12 audio files, ~3–8 min each. With `SYNTHGEN_TTS=pyttsx3` you get free offline audio (single voice); with `openai` you get natural multi-voice calls.

---

## Stage 4 — Whisper transcription (local, no key — or OpenAI API)
```bash
python run.py transcribe     # SYNTHGEN_WHISPER=local downloads a model once
```
**What it does:** transcribes the 12 audios back to text, closing the call-intelligence loop end-to-end (synthetic audio → real STT → transcript), so the call-intel features run on genuinely transcribed text rather than the original script.

**Output:** `out/transcribed/<meeting_id>.txt` ×12.

**Expect:** 12 transcripts. They will differ slightly from the Stage-2 script (that's the point — it exercises the real STT path). `local` runs on the i7 with no spend.

---

## Stage 5 — assemble canonical records + schema validation (offline)
```bash
python run.py assemble
```
**What it does:** merges skeleton structure with expanded bodies and the Whisper transcripts (audio meetings get `origin: whisper`, others `origin: text`), stamps every record with the conventions (`tenant_id`, `external_id=null`, `source`, `confidence`, `freshness`), and validates against `schema/canonical.schema.json`.

**Output:** `out/canonical/*.jsonl`.

**Expect:** counts matching the skeleton, then `schema validation: PASS`. (Runs even before Stages 2–4 — bodies are just empty — so you can validate structure early.)

---

## Stage — validation gate (offline)
```bash
python run.py validate
```
**Expect:** `RESULT: PASS`. Fails the run if any contact/opp/meeting points at a missing parent, if account count or audio count is wrong, or if a closed deal lacks win/loss truth in the ledger.

---

## Stage — source mapping & archive (offline) → see P7
```bash
python run.py map
```
**What it does:** reshapes canonical records into Salesforce / Gmail / Calendar / Slack / Jira payloads and writes per-source archives + a Stage-3 field map. Full detail in `../05_pipeline_mapping/SOURCE_MAPPING_AND_LOAD.md`.

**Expect:**
```
salesforce.Account 10 · salesforce.Contact 54 · salesforce.Opportunity 14
salesforce.Event 68 · salesforce.Task 79 · gmail.messages 118
gcal.events 68 · slack.messages 234 · jira.issues 44
```

---

## Stage 6 — load into the data plane (needs Docker services)
```bash
docker compose up -d postgres minio
python run.py load-postgres      # Salesforce-shaped tables, queryable
python run.py load-minio         # audios + docs into object storage
```
**What it does:** lands canonical data in Postgres (table names mirror Salesforce objects so Stage-3 is a re-point, not a migration) and blobs in MinIO.

**Expect:** row counts per table printed; `out/audio/*` and `doc_*.md` uploaded to the `meetingiq` bucket (browse at MinIO console `localhost:9001`). Sample check:
```sql
SELECT colour, count(*) FROM account GROUP BY colour;          -- green/yellow/red/blue/grey spread
SELECT origin, count(*) FROM transcript GROUP BY origin;        -- 12 whisper, rest text
```

---

## One-shot
```bash
python run.py all     # Stages 1→5 + validate + map  (needs keys for 2–4)
python run.py load-postgres && python run.py load-minio
```

---

## What you have at the end (and what's deliberately *not* done)
**Done:** a connected, validated, multi-source synthetic world in canonical form, in Postgres + MinIO, with per-source archives and a hidden ground-truth ledger.
**Not done (next phase, on purpose):** embeddings, vector/graph indexing, parent-child chunking, the Context Compiler. Plain data only — exactly the handoff point requested.

## Troubleshooting
- `ffmpeg not found` → install it and reopen the shell (Stage 3).
- Whisper model download slow → it caches after first run (Stage 4).
- `psycopg`/`minio` connection refused → `docker compose up -d` first (Stage 6).
- Want a different world → change `SEED`/`DEMO_TODAY`/volume targets in `synthgen/config.py`, re-run from Stage 1.
