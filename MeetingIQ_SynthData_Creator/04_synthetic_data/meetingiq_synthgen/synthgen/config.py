"""Global configuration for the Meeting IQ synthetic-data creator.

Everything that makes a run reproducible lives here. Change SEED or DEMO_TODAY
and the entire world regenerates deterministically.
"""
from __future__ import annotations
import os
from datetime import date, timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass 


# ---- reproducibility ----
SEED = 20260608
TENANT_ID = "rapid7-gtm"


def _monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())

##   ---> Have to ask this 
# Fixed "today" for the demo world. Pinned to the Monday of that week so the
# triage workspace always opens on a Monday morning.
DEMO_TODAY = _monday_of(date(2026, 6, 8))

# How far back history runs, and how far forward upcoming meetings go.
HISTORY_DAYS = 130          # ~Feb -> Jun
UPCOMING_DAYS = 14          # next two weeks

# ---- paths ----
ROOT = Path(__file__).resolve().parent.parent
OUT = Path(os.getenv("SYNTHGEN_OUT", str(ROOT / "out")))
SKELETON = OUT / "skeleton"          # parquet/jsonl skeleton (Stage 1)
ARTIFACTS = OUT / "artifacts"        # transcripts, emails, slack, docs (Stage 2)
AUDIO = OUT / "audio"                # tts wav/mp3 (Stage 3)
TRANSCRIBED = OUT / "transcribed"    # whisper output (Stage 4)
CANONICAL = OUT / "canonical"        # assembled canonical records (Stage 5)
SOURCEMAP = OUT / "source_archive"   # per-source shaped archives (P7)
LEDGER_PATH = OUT / "ground_truth_ledger.json"

for _p in (OUT, SKELETON, ARTIFACTS, AUDIO, TRANSCRIBED, CANONICAL, SOURCEMAP):
    _p.mkdir(parents=True, exist_ok=True)

# ---- provider switches (read from env; see .env.example) ----
LLM_MODEL = os.getenv("SYNTHGEN_LLM_MODEL", "claude-sonnet-4-6")
LLM_HEAVY_MODEL = os.getenv("SYNTHGEN_LLM_HEAVY", "claude-opus-4-8")
TTS_PROVIDER = os.getenv("SYNTHGEN_TTS", "pyttsx3")        # openai | azure | elevenlabs | pyttsx3(offline)
WHISPER_MODE = os.getenv("SYNTHGEN_WHISPER", "local")      # local(faster-whisper) | api(openai)

# ---- volume targets (sanity bounds for the validator) ----
TARGETS = {
    "accounts": 10,
    "users": 7,
    "contacts": (45, 70),
    "opportunities": (12, 20),
    "meetings": (60, 90),
    "audio_meetings": 12,
    "emails": (110, 180),
    "slack_messages": (200, 320),
    "jira_issues": (30, 55),
    "documents": (24, 40),
    "news_items": (15, 28),
}

# Record-level conventions stamped on every canonical record.
RECORD_DEFAULTS = {
    "tenant_id": TENANT_ID,
    "external_id": None,     # Salesforce-shaped slot, filled only at Stage 3
}
