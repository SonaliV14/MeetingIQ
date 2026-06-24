"""Validation harness. Runs after the skeleton (and again after assembly).

Checks: referential integrity, volume targets, audio count, and ledger coverage.
Exits non-zero on failure so it can gate a pipeline.
"""
from __future__ import annotations
import json
import sys
from . import config


def _load(name: str) -> list[dict]:
    p = config.SKELETON / f"{name}.jsonl"
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def _in_range(n: int, bound) -> bool:
    if isinstance(bound, tuple):
        return bound[0] <= n <= bound[1]
    return n == bound


def run() -> int:
    fails, warns = [], []
    t = {name: _load(name) for name in ["users", "accounts", "firmographics", "contacts",
                                        "opportunities", "meetings", "action_items", "emails",
                                        "slack", "jira", "documents", "news"]}
    acc_ids = {a["id"] for a in t["accounts"]}
    opp_ids = {o["id"] for o in t["opportunities"]}
    meet_ids = {m["id"] for m in t["meetings"]}

    # referential integrity
    for c in t["contacts"]:
        if c["account_id"] not in acc_ids:
            fails.append(f"contact {c['id']} -> missing account {c['account_id']}")
    for o in t["opportunities"]:
        if o["account_id"] not in acc_ids:
            fails.append(f"opp {o['id']} -> missing account {o['account_id']}")
    for m in t["meetings"]:
        if m["account_id"] not in acc_ids:
            fails.append(f"meeting {m['id']} -> missing account")
        if m["opportunity_id"] and m["opportunity_id"] not in opp_ids:
            fails.append(f"meeting {m['id']} -> missing opp {m['opportunity_id']}")
    for ai in t["action_items"]:
        if ai["meeting_id"] and ai["meeting_id"] not in meet_ids:
            fails.append(f"action {ai['id']} -> missing meeting")

    # target bounds (map target keys -> entity count keys)
    counts = {k: len(v) for k, v in t.items()}
    counts["audio_meetings"] = sum(1 for m in t["meetings"] if m.get("audio"))
    target_key_map = {"slack_messages": "slack", "jira_issues": "jira", "news_items": "news"}
    for key, bound in config.TARGETS.items():
        ckey = target_key_map.get(key, key)
        n = counts.get(ckey, 0)
        if not _in_range(n, bound):
            (fails if key in ("accounts", "audio_meetings") else warns).append(
                f"{key}={n} outside target {bound}")

    # ledger coverage: every non-steady deal has >=1 planted signal; closed deals have win_loss
    if config.LEDGER_PATH.exists():
        ledger = json.loads(config.LEDGER_PATH.read_text())
        for d in ledger:
            if not d["planted_signals"]:
                warns.append(f"ledger {d['deal_id']} has no planted signals")
            if d["true_stage"].startswith("Closed") and not d["win_loss"]:
                fails.append(f"ledger {d['deal_id']} closed but no win_loss truth")
    else:
        fails.append("ground-truth ledger missing")

    # report
    print("=== VALIDATION ===")
    print("counts:", json.dumps(counts))
    for w in warns:
        print("  WARN:", w)
    for f in fails:
        print("  FAIL:", f)
    ok = not fails
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(run())
