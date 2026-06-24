# Meeting IQ — Synthetic Data Creator (compiled bundle)

A self-contained handoff for generating the **Rapid7 synthetic world** — plain,
source-shaped, validated data plus a hidden ground-truth ledger — ready to load
into Postgres + MinIO **before** the context layer (embedding/graph/chunking).

## What's inside
```
03_client_scenario/SCENARIO_RAPID7.md        # the world: 10 accounts, committees,
                                             #   deal arcs, planted signals, ledger
04_synthetic_data/
  ENV_AND_REQUIREMENTS.md                    # P5 — Win 11 setup (Rust/Polars, Docker, keys)
  SYNTHETIC_DATA_BUILD.md                    # P6 — step-by-step runbook + what to expect
  meetingiq_synthgen/                        # the runnable package (code + schema + compose)
05_pipeline_mapping/SOURCE_MAPPING_AND_LOAD.md  # P7 — canonical→source archives + DB load
```

## Start here
1. Read `04_synthetic_data/ENV_AND_REQUIREMENTS.md` and set up the toolchain.
2. `cd 04_synthetic_data/meetingiq_synthgen` and follow its `README.md`.
3. Prove it offline first:
   ```bash
   pip install -r requirements.txt
   python run.py skeleton      # deterministic, no keys
   python run.py validate      # expect: RESULT: PASS
   python run.py map           # writes Salesforce/Gmail/Slack/Jira archives
   ```
4. Add keys (`.env`) and run the LLM/TTS/Whisper stages, then load into Docker
   (Postgres + MinIO). The full runbook is `SYNTHETIC_DATA_BUILD.md`.

## Verified before shipping
The offline stages were executed end-to-end: **10 accounts · 54 contacts ·
14 opportunities · 68 meetings · 12 audio calls · 118 emails · 234 Slack ·
44 Jira · 30 docs · 23 news · 10 ledger deals → validation PASS**, schema
validation PASS, and the source mapper produced Salesforce-shaped objects with a
Stage-3 field map. The LLM/TTS/Whisper stages are real code that runs on your
machine with the relevant keys.

## Scope boundary (by design)
This produces **plain synthetic data only**. Embeddings, vector/graph indexing,
chunking, and the Context Compiler are the *next* phase and are intentionally not
included here.

*All companies and people in the data are fictional; Rapid7's real public products
are modelled for realism.*
