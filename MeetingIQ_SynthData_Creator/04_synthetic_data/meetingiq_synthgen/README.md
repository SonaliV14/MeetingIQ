# Meeting IQ — Synthetic Data Creator

Generates the **Rapid7 synthetic world** (see `../03_client_scenario/SCENARIO_RAPID7.md`)
as plain, source-shaped data — ready to load into Postgres + MinIO **before** the
context layer (embedding / graph / chunking come later). It produces a connected
world of accounts, contacts, opportunities, meetings, transcripts (incl. 12 real
TTS→Whisper calls), emails, Slack, Jira, documents and news, **plus a hidden
ground-truth ledger** that evals score against.

## Pipeline (stages)
| Stage | Command | Needs | Output |
|---|---|---|---|
| 1 Skeleton | `python run.py skeleton` | nothing (offline) | `out/skeleton/*` + ledger |
| 2 Expand (LLM) | `python run.py expand` | `ANTHROPIC_API_KEY` | `out/artifacts/*` (transcripts, emails, docs) |
| 3 TTS | `python run.py tts` | TTS provider key | `out/audio/*.mp3` (the 12 calls) |
| 4 Transcribe | `python run.py transcribe` | local whisper or `OPENAI_API_KEY` | `out/transcribed/*.txt` |
| 5 Assemble | `python run.py assemble` | nothing | `out/canonical/*` (+ schema validation) |
| — Validate | `python run.py validate` | nothing | PASS/FAIL gate |
| — Map (P7) | `python run.py map` | nothing | `out/source_archive/{salesforce,gmail,gcal,slack,jira}` |
| 6a Load DB | `python run.py load-postgres` | Postgres | tables in Postgres |
| 6b Load blobs | `python run.py load-minio` | MinIO | objects in MinIO |
| all | `python run.py all` | keys for 2–4 | full run |

## Quick start (Windows 11 — see `../ENV_AND_REQUIREMENTS.md`)
```bash
python -m venv .venv && .venv\Scripts\activate     # or use uv
pip install -r requirements.txt
copy .env.example .env                              # fill in keys you need

python run.py skeleton        # works offline, deterministic — try this first
python run.py validate        # should print RESULT: PASS

docker compose up -d          # Postgres + MinIO
# fill ANTHROPIC_API_KEY + TTS key in .env, then:
python run.py all
python run.py load-postgres && python run.py load-minio
```

## Reproducibility
Everything keys off `SEED` and `DEMO_TODAY` in `synthgen/config.py`. Same seed ⇒
byte-identical skeleton. Stages 2–4 are LLM/TTS and so vary; they are idempotent
(skip artifacts that already exist), so a re-run only fills gaps.

## What "good" looks like after `skeleton` + `validate`
~10 accounts · ~54 contacts · ~14 opportunities · ~68 meetings · **12 audio** ·
~118 emails · ~234 Slack · ~44 Jira · ~30 docs · ~23 news · 10 ledger deals →
`RESULT: PASS`.

## Layout
```
run.py                     # CLI orchestrator
synthgen/
  config.py                # seed, DEMO_TODAY, paths, targets, provider switches
  accounts.py              # the 10 accounts, committees, products, signal taxonomy
  schema.py                # Pydantic canonical models
  skeleton.py              # Stage 1 (Polars + Faker)
  ledger.py                # ground-truth ledger
  expand_llm.py            # Stage 2 (Anthropic)
  tts.py                   # Stage 3 (TTS, pluggable)
  transcribe.py            # Stage 4 (Whisper)
  assemble.py              # Stage 5 (+ JSON-schema validation)
  validate.py              # integrity / target / ledger checks
  source_map.py            # P7 — per-source archives + Stage-3 field map
  load_postgres.py         # Stage 6a
  load_minio.py            # Stage 6b
schema/canonical.schema.json
docker-compose.yml  Makefile  requirements.txt  .env.example
```
The full step-by-step walkthrough with "what to expect" at each step is in
`../SYNTHETIC_DATA_BUILD.md`.
