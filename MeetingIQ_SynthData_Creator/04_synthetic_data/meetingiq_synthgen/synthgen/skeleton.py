"""Stage 1 — deterministic skeleton (Polars + Faker, fixed seed).

Builds the *structure* of the world: users, accounts, firmographics, contacts,
opportunities, meeting skeletons, action items, and stubs for emails/slack/jira/
docs/news (bodies are empty here; Stage 2 LLM-expands them). Also seeds the
ground-truth ledger with the planted-signal plan per deal.

Output: out/skeleton/*.jsonl (+ parquet for the tabular core) and the ledger.
Re-running with the same SEED reproduces byte-identical structure.
"""
from __future__ import annotations
import json
import random
from datetime import datetime, timedelta

import polars as pl
from faker import Faker

from . import config
from .accounts import (ACCOUNTS, USERS, HERO_COMMITTEES, ROLE_TEMPLATE, BANDS,
                       MEETING_ARC)
from .ledger import Ledger, DealLedger

fake = Faker()

# meeting arc slice per deal state
STATE_ARC = {
    "open_new":        ["sdr_qualification", "discovery", "technical_demo", "poc_kickoff"],
    "open_advancing":  ["discovery", "technical_demo", "poc_kickoff", "poc_checkin", "poc_results_business_case", "pricing_packaging"],
    "at_risk":         ["discovery", "technical_demo", "poc_kickoff", "poc_checkin", "poc_results_business_case", "pricing_packaging", "negotiation"],
    "closed_won":      ["discovery", "technical_demo", "poc_kickoff", "poc_results_business_case", "pricing_packaging", "negotiation", "close_or_loss_debrief"],
    "closed_lost":     ["discovery", "technical_demo", "poc_kickoff", "poc_results_business_case", "pricing_packaging", "close_or_loss_debrief"],
    "expansion":       ["discovery", "technical_demo", "poc_results_business_case"],
    "steady":          ["recurring_sync", "recurring_sync", "recurring_sync"],
}
RECORDED_TYPES = {t for t, rec in MEETING_ARC if rec} | {"recurring_sync"}
STAGE_BY_STATE = {
    "open_new": "Discovery", "open_advancing": "Technical Validation",
    "at_risk": "Negotiation (stalled)", "closed_won": "Closed Won",
    "closed_lost": "Closed Lost", "expansion": "Expansion", "steady": "Customer Success",
}


def _seed() -> None:
    random.seed(config.SEED)
    Faker.seed(config.SEED)


def _meeting_dates(n: int, state: str) -> list[datetime]:
    """Spread n meetings; open deals push the last 1-2 into the future."""
    today = datetime(config.DEMO_TODAY.year, config.DEMO_TODAY.month, config.DEMO_TODAY.day, 10, 0)
    if state in ("closed_won", "closed_lost"):
        start = today - timedelta(days=config.HISTORY_DAYS)
        end = today - timedelta(days=18)
        future = 0
    elif state == "steady":
        # monthly-ish touches around today
        base = today - timedelta(days=40)
        return [base + timedelta(days=30 * i, hours=random.randint(-2, 5)) for i in range(n)]
    else:  # open / expansion
        start = today - timedelta(days=config.HISTORY_DAYS)
        end = today + timedelta(days=config.UPCOMING_DAYS)
        future = 1 if state == "open_new" else 2
    span = (end - start).days
    past_n = n - future
    dates = []
    for i in range(past_n):
        d = start + timedelta(days=int(span * (i / max(past_n, 1)) * 0.7) + random.randint(0, 4))
        dates.append(d.replace(hour=random.choice([9, 11, 14, 15]), minute=0))
    for j in range(future):
        d = today + timedelta(days=2 + j * 5 + random.randint(0, 2))
        dates.append(d.replace(hour=random.choice([10, 13]), minute=0))
    return sorted(dates)


def _committee(acc: dict) -> list[dict]:
    if acc["code"] in HERO_COMMITTEES:
        return HERO_COMMITTEES[acc["code"]]
    out = []
    for role, power in ROLE_TEMPLATE:
        band = {"economic_buyer": "C-level", "champion": "Director",
                "blocker": "Manager", "influencer": "Director"}.get(role, "Manager")
        out.append({"name": fake.name(), "title": f"{role.replace('_', ' ').title()}",
                    "band": band, "role": role, "power": power, "sentiment_arc": ["neutral"]})
    return out


def build() -> dict[str, list[dict]]:
    _seed()
    led = Ledger()
    users = [dict(id=f"U{i+1}", source="crm", tenant_id=config.TENANT_ID, **u) for i, u in enumerate(USERS)]
    ae = next(u for u in users if u["role"] == "Enterprise AE")["id"]

    accounts, firmographics, contacts, opps, meetings = [], [], [], [], []
    action_items, emails, slack, jira, docs, news = [], [], [], [], [], []
    audio_budget = config.TARGETS["audio_meetings"]
    audio_count = 0

    # account priority order for audio assignment (hero/active first)
    order = sorted(ACCOUNTS, key=lambda a: (not a["hero"], a["state"] not in ("open_advancing", "at_risk")))

    for acc in ACCOUNTS:
        aid = acc["code"]
        accounts.append(dict(id=aid, source="crm", tenant_id=config.TENANT_ID, code=aid,
                             name=acc["name"], vertical=acc["vertical"], size=acc["size"],
                             colour=acc["colour"], state=acc["state"]))
        firmographics.append(dict(id=f"FIRM-{aid}", source="news", account_id=aid,
                                  vertical=acc["vertical"], employee_band=f"{acc['size']:,}",
                                  region=fake.country(), profile=f"{acc['vertical']} org, ~{acc['size']} staff"))
        comm = _committee(acc)
        cids = []
        for k, c in enumerate(comm):
            cid = f"{aid}-C{k+1}"
            cids.append(cid)
            contacts.append(dict(id=cid, source="crm", account_id=aid, name=c["name"], title=c["title"],
                                 band=c["band"], committee_role=c["role"], decision_power=c["power"],
                                 email=f"{c['name'].lower().replace(' ', '.')}@{acc['name'].lower().replace(' ', '')}.example"))

        # opportunity
        oid = f"{aid}-OPP1"
        is_closed = acc["state"].startswith("closed")
        opps.append(dict(id=oid, source="crm", account_id=aid, name=f"{acc['name']} - {acc['products'][0]}",
                         stage=STAGE_BY_STATE[acc["state"]], products=acc["products"], acv=acc["acv"],
                         owner_user_id=ae, is_closed=is_closed, is_won=acc["state"] == "closed_won"))

        # meetings from the state arc
        arc = STATE_ARC[acc["state"]]
        dates = _meeting_dates(len(arc), acc["state"])
        deal_meetings = []
        for k, (mtype, dt) in enumerate(zip(arc, dates)):
            mid = f"{aid}-M{k+1}"
            recorded = mtype in RECORDED_TYPES
            audio = False
            if recorded and audio_count < audio_budget and acc in order[:6]:
                audio = True
                audio_count += 1
            internal = mtype in ("close_or_loss_debrief",)
            meetings.append(dict(id=mid, source="gcal", account_id=aid, opportunity_id=oid,
                                 title=f"{acc['name']}: {mtype.replace('_', ' ').title()}",
                                 meeting_type=mtype, channel="internal" if internal else random.choice(["zoom", "gmeet"]),
                                 attendee_user_ids=[ae] + ([] if mtype == "sdr_qualification" else ["U2"]),
                                 attendee_contact_ids=cids[: min(3, len(cids))],
                                 recorded=recorded, audio=audio, start=dt.isoformat(), duration_min=random.choice([30, 45, 60])))
            deal_meetings.append((mid, mtype, dt))
            # action items
            for ai in range(random.randint(1, 2)):
                action_items.append(dict(id=f"{mid}-T{ai+1}", source="crm", account_id=aid, meeting_id=mid,
                                         title=f"Follow up after {mtype}", owner=ae, status="open",
                                         due=(dt + timedelta(days=3)).isoformat()))
            # email stubs: recap + scheduling
            emails.append(dict(id=f"{mid}-E-recap", source="gmail", thread_id=f"{aid}-thread", account_id=aid,
                               subject=f"Recap: {mtype.replace('_', ' ')}", from_addr="priya.menon@rapid7.example",
                               to_addrs=[contacts[-1]["email"]], body=""))
            emails.append(dict(id=f"{mid}-E-sched", source="gmail", thread_id=f"{aid}-sched", account_id=aid,
                               subject=f"Scheduling: {mtype.replace('_', ' ')}", from_addr="priya.menon@rapid7.example",
                               to_addrs=[contacts[-1]["email"]], body=""))

        # internal war-room / manager syncs (not recorded, internal channel)
        n_sync = 2 if acc["state"] in ("open_advancing", "at_risk", "closed_won", "closed_lost") else (1 if acc["state"] in ("open_new", "expansion") else 0)
        for sci in range(n_sync):
            sdt = dates[min(sci + 1, len(dates) - 1)] - timedelta(days=1)
            meetings.append(dict(id=f"{aid}-IS{sci+1}", source="gcal", account_id=aid, opportunity_id=oid,
                                 title=f"{acc['name']}: internal deal sync", meeting_type="internal_sync",
                                 channel="internal", attendee_user_ids=[ae, "U2", "U4"], attendee_contact_ids=[],
                                 recorded=False, audio=False, start=sdt.isoformat(), duration_min=30))

        # intro thread + at-risk 'quiet' thread + procurement thread
        emails.append(dict(id=f"{aid}-E-intro", source="gmail", thread_id=f"{aid}-intro", account_id=aid,
                           subject=f"Intro: Rapid7 x {acc['name']}", from_addr="tom.becker@rapid7.example",
                           to_addrs=[contacts[-3]["email"]], body=""))
        if acc["state"] == "at_risk":
            emails.append(dict(id=f"{aid}-E-quiet", source="gmail", thread_id=f"{aid}-quiet", account_id=aid,
                               subject="Checking in", from_addr="priya.menon@rapid7.example",
                               to_addrs=[contacts[1]["email"]], body=""))

        # slack channel + messages
        chan = f"#deal-{acc['name'].split()[0].lower()}"
        for m in range(random.randint(18, 30)):
            slack.append(dict(id=f"{aid}-S{m+1}", source="slack", channel_name=chan, account_id=aid,
                              author=random.choice([u["name"] for u in users[:5]]), body=""))

        # jira issues (POC tasks)
        for j in range(random.randint(3, 5)):
            jira.append(dict(id=f"{aid}-J{j+1}", source="jira", account_id=aid,
                             title=f"POC task {j+1} for {acc['name']}", owner="dev.sharma@rapid7.example",
                             status=random.choice(["open", "in_progress", "done"])))

        # documents
        for dt_type in ["proposal", "battlecard", "poc_criteria"]:
            docs.append(dict(id=f"{aid}-DOC-{dt_type}", source="doc", account_id=aid, doc_type=dt_type,
                             title=f"{acc['name']} {dt_type.replace('_', ' ')}", body=""))
        # news (2 per account, +1 for hero accounts)
        for ni in range(2 + (1 if acc["hero"] else 0)):
            news.append(dict(id=f"{aid}-NEWS{ni+1}", source="news", account_id=aid,
                             headline=f"{acc['vertical']} sector security news ({ni+1})", body=""))

        # ---- ledger: plant the signal plan for this deal ----
        risk = {"open_advancing": 28, "open_new": 45, "at_risk": 78, "closed_won": 10,
                "closed_lost": 90, "expansion": 22, "steady": 30}[acc["state"]]
        d = led.add(DealLedger(deal_id=oid, account=acc["name"], true_stage=STAGE_BY_STATE[acc["state"]],
                               true_risk_score=risk, true_trajectory=acc["trajectory"], competitor=acc["competitor"]))
        mids = [m[0] for m in deal_meetings]
        if acc["competitor"]:
            d.plant(mids[0], "competitor_mention", "-", f"Incumbent {acc['competitor']} mentioned")
            d.plant(mids[0], "incumbent_loyalty", "-", f"Long-standing {acc['competitor']} use")
        d.plant(mids[min(1, len(mids)-1)], "need_signal", "+", "Pain point that maps to the product")
        if acc["state"] in ("at_risk", "closed_lost"):
            d.plant(mids[-1], "budget_signal", "-", "Budget frozen / not this quarter")
            d.plant(mids[-1], "sentiment_shift", "-", "Champion / buyer cooling")
        if acc["state"] == "at_risk":
            d.plant(mids[-1], "champion_change", "-", "Champion losing influence")
        if acc["state"] in ("open_advancing", "closed_won"):
            d.plant(mids[-1], "timing_signal", "+", "Wants live before a compliance deadline")
            d.plant(mids[1], "commitment", "+", "Customer commits to share asset inventory")
        d.bant_truth = {"budget": "partial" if acc["state"] != "closed_won" else "known",
                        "authority": "known", "need": "known", "timing": "known" if acc["trajectory"] != "flat" else "partial"}
        if is_closed:
            d.win_loss = {"outcome": "won" if acc["state"] == "closed_won" else "lost",
                          "reasons": (["clear ROI", "strong POC"] if acc["state"] == "closed_won"
                                      else [f"{acc['competitor']} incumbency", "weak technical demo", "late exec sponsor"])}
        d.committee_coverage_truth = {c["committee_role"]: "engaged" for c in [contacts[i] for i, _ in enumerate(comm)]}

    # second opps for a few accounts to hit the opp target
    for aid in ["A1", "A2", "A7", "A9"]:
        acc = next(a for a in ACCOUNTS if a["code"] == aid)
        opps.append(dict(id=f"{aid}-OPP2", source="crm", account_id=aid,
                         name=f"{acc['name']} - Expansion ({acc['products'][-1]})",
                         stage="Expansion", products=[acc["products"][-1]], acv=int(acc["acv"] * 0.4),
                         owner_user_id=ae, is_closed=False, is_won=False))

    tables = dict(users=users, accounts=accounts, firmographics=firmographics, contacts=contacts,
                  opportunities=opps, meetings=meetings, action_items=action_items, emails=emails,
                  slack=slack, jira=jira, documents=docs, news=news)

    # write outputs: jsonl for everything + parquet for the tabular core (Polars)
    for name, rows in tables.items():
        (config.SKELETON / f"{name}.jsonl").write_text("\n".join(json.dumps(r, default=str) for r in rows))
    for name in ["accounts", "contacts", "opportunities", "meetings"]:
        pl.DataFrame(tables[name]).write_parquet(config.SKELETON / f"{name}.parquet")
    led.save()

    summary = {k: len(v) for k, v in tables.items()}
    summary["audio_meetings"] = sum(1 for m in meetings if m["audio"])
    summary["ledger_deals"] = len(led.deals)
    (config.SKELETON / "_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    s = build()
    print("Skeleton built. Counts:")
    for k, v in s.items():
        print(f"  {k:20s} {v}")
