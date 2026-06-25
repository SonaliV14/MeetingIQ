"""Stage 2 — LLM expansion (Anthropic).

Turns skeleton stubs into rich artifacts and *weaves in the planted signals* from
the ground-truth ledger, so extraction/scoring has real material to find. Requires
ANTHROPIC_API_KEY. Cheap model for bulk (transcripts/emails), heavy model optional.

Idempotent: skips an artifact if its output file already exists.

All output files are written as UTF-8 so downstream stages (tts.py, transcribe.py)
can read them reliably on Windows without cp1252 / encoding issues.
"""
from __future__ import annotations
import json
import os
from . import config
from .ledger import Ledger

try:
    import anthropic
except ImportError:
    anthropic = None


def _client():
    if anthropic is None:
        raise RuntimeError("pip install anthropic")
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("set ANTHROPIC_API_KEY in your .env file")
    return anthropic.Anthropic()


def _load(name):
    p = config.SKELETON / f"{name}.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def _write(path, text: str) -> None:
    """Write text as UTF-8 explicitly — avoids cp1252 on Windows."""
    path.write_text(text, encoding="utf-8")


def _signals_for_meeting(ledger: Ledger, meeting_id: str) -> list[dict]:
    out = []
    for d in ledger.deals.values():
        out += [s for s in d.planted_signals if s["meeting_id"] == meeting_id]
    return out


TRANSCRIPT_SYS = (
    "You write realistic B2B SaaS sales-call transcripts for a synthetic dataset. "
    "Speakers are named. Keep it natural, 3-8 minutes of dialogue. You MUST embed each "
    "provided signal naturally as something a participant says. Do not label the signals."
)


def expand_transcripts(limit: int | None = None) -> int:
    client = _client()
    ledger = Ledger.load()
    meetings = _load("meetings")
    contacts = {c["id"]: c for c in _load("contacts")}
    users = {u["id"]: u for u in _load("users")}
    n = 0
    for m in meetings:
        if m["meeting_type"] == "internal_sync":
            continue
        out_path = config.ARTIFACTS / f"transcript_{m['id']}.txt"
        if out_path.exists():
            continue
        speakers = [users[u]["name"] for u in m["attendee_user_ids"] if u in users]
        speakers += [contacts[c]["name"] for c in m["attendee_contact_ids"] if c in contacts]
        sigs = _signals_for_meeting(ledger, m["id"])
        sig_lines = "\n".join(f"- {s['type']} ({s['polarity']}): {s['text_hint']}" for s in sigs) or "- (no required signals)"
        prompt = (f"Meeting: {m['title']} ({m['meeting_type']}).\nSpeakers: {', '.join(speakers)}.\n"
                  f"Signals to embed naturally:\n{sig_lines}\n\nWrite the transcript now.")
        msg = client.messages.create(model=config.LLM_MODEL, max_tokens=1500,
                                     system=TRANSCRIPT_SYS, messages=[{"role": "user", "content": prompt}])
        _write(out_path, msg.content[0].text)
        n += 1
        if limit and n >= limit:
            break
    return n


EMAIL_SYS = "You write concise, realistic B2B sales emails for a synthetic dataset. No signatures beyond a name."


def expand_emails(limit: int | None = None) -> int:
    client = _client()
    emails = _load("emails")
    n = 0
    for e in emails:
        out_path = config.ARTIFACTS / f"email_{e['id']}.txt"
        if out_path.exists():
            continue
        prompt = f"Subject: {e['subject']}\nFrom: {e['from_addr']}\nTo: {', '.join(e['to_addrs'])}\nWrite the email body."
        msg = client.messages.create(model=config.LLM_MODEL, max_tokens=400,
                                     system=EMAIL_SYS, messages=[{"role": "user", "content": prompt}])
        _write(out_path, msg.content[0].text)
        n += 1
        if limit and n >= limit:
            break
    return n


def expand_documents(limit: int | None = None) -> int:
    client = _client()
    docs = _load("documents")
    n = 0
    sys_prompt = "You write short B2B security sales documents for a synthetic dataset (1-2 pages of markdown)."
    for d in docs:
        out_path = config.ARTIFACTS / f"doc_{d['id']}.md"
        if out_path.exists():
            continue
        prompt = f"Document type: {d['doc_type']}. Title: {d['title']}. Write it."
        msg = client.messages.create(model=config.LLM_MODEL, max_tokens=1200,
                                     system=sys_prompt, messages=[{"role": "user", "content": prompt}])
        _write(out_path, msg.content[0].text)
        n += 1
        if limit and n >= limit:
            break
    return n


if __name__ == "__main__":
    print("transcripts:", expand_transcripts())
    print("emails:", expand_emails())
    print("documents:", expand_documents())