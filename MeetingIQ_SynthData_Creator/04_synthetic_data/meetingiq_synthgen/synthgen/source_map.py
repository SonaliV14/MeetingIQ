"""P7 — source-system mapping & archive.

Reshapes canonical records into the exact shapes their real source systems use, and
archives them per-source. This does two jobs:
  1. Realises the *ingestion-adapter contract* in reverse — proving each connector's
     payload maps 1:1 to the canonical schema (and back).
  2. Produces the Stage-3 field map: the provisional Salesforce ids that would
     populate `external_id` when the CRM MCP is re-pointed at real Salesforce.

Pure reshaping — no API keys, no services. Runs on the assembled canonical records.
"""
from __future__ import annotations
import json
from . import config

ARCHIVE = config.SOURCEMAP


def _load(name):
    p = config.CANONICAL / f"{name}.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def _write(source: str, rows: list[dict]):
    d = ARCHIVE / source
    d.mkdir(parents=True, exist_ok=True)
    (d / "records.jsonl").write_text("\n".join(json.dumps(r, default=str) for r in rows))


# ---- Salesforce-shaped ids (the Stage-3 external_id slots) ----
def _sfid(prefix: str, n: int) -> str:
    return f"{prefix}{n:012d}"


# ---- mappers (canonical -> source shape) ----
def map_salesforce(accounts, contacts, opps, meetings, tasks):
    field_map = {"account_id_to_sf": {}, "contact_id_to_sf": {}, "opp_id_to_sf": {}}
    sf = {"Account": [], "Contact": [], "Opportunity": [], "Event": [], "Task": []}
    for i, a in enumerate(accounts):
        sfid = _sfid("001", i + 1)
        field_map["account_id_to_sf"][a["id"]] = sfid
        sf["Account"].append({"Id": sfid, "Name": a["name"], "Industry": a["vertical"],
                              "NumberOfEmployees": a["size"], "Meeting_IQ_State__c": a["state"]})
    for i, c in enumerate(contacts):
        sfid = _sfid("003", i + 1)
        field_map["contact_id_to_sf"][c["id"]] = sfid
        sf["Contact"].append({"Id": sfid, "AccountId": field_map["account_id_to_sf"].get(c["account_id"]),
                              "LastName": c["name"].split()[-1], "FirstName": c["name"].split()[0],
                              "Title": c["title"], "Email": c["email"],
                              "Committee_Role__c": c["committee_role"], "Decision_Power__c": c["decision_power"]})
    for i, o in enumerate(opps):
        sfid = _sfid("006", i + 1)
        field_map["opp_id_to_sf"][o["id"]] = sfid
        sf["Opportunity"].append({"Id": sfid, "AccountId": field_map["account_id_to_sf"].get(o["account_id"]),
                                  "Name": o["name"], "StageName": o["stage"], "Amount": o["acv"],
                                  "IsClosed": o.get("is_closed", False), "IsWon": o.get("is_won", False)})
    for i, m in enumerate(meetings):
        sf["Event"].append({"Id": _sfid("00U", i + 1), "Subject": m["title"], "StartDateTime": m["start"],
                            "DurationInMinutes": m.get("duration_min", 30),
                            "WhatId": field_map["opp_id_to_sf"].get(m.get("opportunity_id")),
                            "Meeting_Type__c": m["meeting_type"], "Was_Recorded__c": m.get("recorded", False)})
    for i, t in enumerate(tasks):
        sf["Task"].append({"Id": _sfid("00T", i + 1), "Subject": t["title"], "Status": t["status"],
                           "ActivityDate": t.get("due")})
    for obj, rows in sf.items():
        _write(f"salesforce/{obj}", rows)
    (ARCHIVE / "salesforce" / "field_map.json").write_text(json.dumps(field_map, indent=2))
    return {f"salesforce.{k}": len(v) for k, v in sf.items()}


def map_gmail(emails):
    rows = [{"id": e["id"], "threadId": e["thread_id"],
             "payload": {"headers": [{"name": "Subject", "value": e["subject"]},
                                     {"name": "From", "value": e["from_addr"]},
                                     {"name": "To", "value": ", ".join(e["to_addrs"])}],
                         "body": {"data": e.get("body", "")}}} for e in emails]
    _write("gmail", rows)
    return {"gmail.messages": len(rows)}


def map_gcal(meetings):
    rows = [{"id": m["id"], "summary": m["title"], "start": {"dateTime": m["start"]},
             "attendees": [{"email": f"user:{u}"} for u in m["attendee_user_ids"]] +
                          [{"email": f"contact:{c}"} for c in m["attendee_contact_ids"]],
             "conferenceData": {"type": m["channel"]}} for m in meetings]
    _write("gcal", rows)
    return {"gcal.events": len(rows)}


def map_slack(messages):
    rows = [{"channel": s["channel_name"], "ts": s["id"], "user": s["author"], "text": s.get("body", "")}
            for s in messages]
    _write("slack", rows)
    return {"slack.messages": len(rows)}


def map_jira(issues):
    rows = [{"key": j["id"], "fields": {"summary": j["title"], "status": {"name": j["status"]},
             "assignee": {"emailAddress": j.get("owner")}}} for j in issues]
    _write("jira", rows)
    return {"jira.issues": len(rows)}


def run() -> dict:
    counts = {}
    counts.update(map_salesforce(_load("accounts"), _load("contacts"), _load("opportunities"),
                                 _load("meetings"), _load("action_items")))
    counts.update(map_gmail(_load("emails")))
    counts.update(map_gcal(_load("meetings")))
    counts.update(map_slack(_load("slack")))
    counts.update(map_jira(_load("jira")))
    (ARCHIVE / "_summary.json").write_text(json.dumps(counts, indent=2))
    return counts


if __name__ == "__main__":
    for k, v in run().items():
        print(f"  {k:24s} {v}")
