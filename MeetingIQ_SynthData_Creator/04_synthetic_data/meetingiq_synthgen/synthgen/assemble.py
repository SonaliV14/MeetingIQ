"""Stage 5 — assemble canonical records.

Merges the skeleton (structure) with the expanded artifacts (bodies) and the
Whisper transcripts (for audio meetings), producing validated canonical records
per entity. For audio meetings the transcript origin is 'whisper'; otherwise 'text'.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from . import config


def _load(name):
    p = config.SKELETON / f"{name}.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def _read(path, default=""):
    return path.read_text() if path.exists() else default


def _stamp(rec: dict, source: str) -> dict:
    rec.setdefault("tenant_id", config.TENANT_ID)
    rec.setdefault("external_id", None)
    rec.setdefault("source", source)
    rec.setdefault("confidence", 1.0)
    rec.setdefault("freshness", datetime.now(timezone.utc).isoformat())
    return rec


def assemble() -> dict[str, int]:
    out_counts = {}

    # pass through structural entities, stamping conventions
    for name, source in [("users", "crm"), ("accounts", "crm"), ("firmographics", "news"),
                         ("contacts", "crm"), ("opportunities", "crm"), ("meetings", "gcal"),
                         ("action_items", "crm"), ("slack", "slack"), ("jira", "jira"), ("news", "news")]:
        rows = [_stamp(r, source) for r in _load(name)]
        (config.CANONICAL / f"{name}.jsonl").write_text("\n".join(json.dumps(r, default=str) for r in rows))
        out_counts[name] = len(rows)

    # transcripts: text (from artifacts) or whisper (from transcribed) per meeting
    transcripts = []
    for m in _load("meetings"):
        if m["meeting_type"] == "internal_sync":
            continue
        if m.get("audio") and (config.TRANSCRIBED / f"{m['id']}.txt").exists():
            text, origin = _read(config.TRANSCRIBED / f"{m['id']}.txt"), "whisper"
        else:
            text, origin = _read(config.ARTIFACTS / f"transcript_{m['id']}.txt"), "text"
        transcripts.append(_stamp(dict(id=f"TR-{m['id']}", meeting_id=m["id"], text=text, origin=origin), "call"))
    (config.CANONICAL / "transcripts.jsonl").write_text("\n".join(json.dumps(r, default=str) for r in transcripts))
    out_counts["transcripts"] = len(transcripts)

    # emails & documents: attach expanded bodies
    emails = []
    for e in _load("emails"):
        e["body"] = _read(config.ARTIFACTS / f"email_{e['id']}.txt")
        emails.append(_stamp(e, "gmail"))
    (config.CANONICAL / "emails.jsonl").write_text("\n".join(json.dumps(r, default=str) for r in emails))
    out_counts["emails"] = len(emails)

    docs = []
    for d in _load("documents"):
        d["body"] = _read(config.ARTIFACTS / f"doc_{d['id']}.md")
        docs.append(_stamp(d, "doc"))
    (config.CANONICAL / "documents.jsonl").write_text("\n".join(json.dumps(r, default=str) for r in docs))
    out_counts["documents"] = len(docs)

    (config.CANONICAL / "_summary.json").write_text(json.dumps(out_counts, indent=2))
    return out_counts


def validate_schema() -> int:
    """Validate assembled records against the canonical JSON schema (structural keys)."""
    import jsonschema
    schema = json.loads((config.ROOT / "schema" / "canonical.schema.json").read_text())
    defs = schema["definitions"]
    entity_map = {"accounts": "Account", "contacts": "Contact", "opportunities": "Opportunity",
                  "meetings": "Meeting", "transcripts": "Transcript", "emails": "Email"}
    errors = 0
    for fname, defname in entity_map.items():
        p = config.CANONICAL / f"{fname}.jsonl"
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            if not line.strip():
                continue
            try:
                jsonschema.validate(json.loads(line), {**schema, "$ref": f"#/definitions/{defname}"})
            except jsonschema.ValidationError as ex:
                errors += 1
                if errors <= 5:
                    print(f"  SCHEMA FAIL [{defname}]: {ex.message}")
    print("schema validation:", "PASS" if errors == 0 else f"{errors} errors")
    return errors


if __name__ == "__main__":
    print("assembled:", assemble())
