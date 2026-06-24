"""The hidden ground-truth ledger: the answer key evals score against.

It is written *as* signals are planted (never reverse-engineered). One row per
deal; the product never reads this file.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from typing import Any
from . import config


@dataclass
class DealLedger:
    deal_id: str
    account: str
    true_stage: str
    true_risk_score: int
    true_trajectory: str                      # improving | flat | declining | na
    competitor: str | None = None
    bant_truth: dict[str, Any] = field(default_factory=dict)
    meddicc_truth: dict[str, Any] = field(default_factory=dict)
    win_loss: dict[str, Any] = field(default_factory=dict)
    planted_signals: list[dict[str, Any]] = field(default_factory=list)
    commitments: list[dict[str, Any]] = field(default_factory=list)
    commercial_significance: list[dict[str, Any]] = field(default_factory=list)
    committee_coverage_truth: dict[str, str] = field(default_factory=dict)

    def plant(self, meeting_id: str, signal_type: str, polarity: str, text_hint: str,
              expected_extraction: str | None = None) -> None:
        self.planted_signals.append({
            "meeting_id": meeting_id, "type": signal_type, "polarity": polarity,
            "text_hint": text_hint, "expected_extraction": expected_extraction,
        })


class Ledger:
    def __init__(self) -> None:
        self.deals: dict[str, DealLedger] = {}

    def add(self, d: DealLedger) -> DealLedger:
        self.deals[d.deal_id] = d
        return d

    def save(self, path=config.LEDGER_PATH) -> None:
        path.write_text(json.dumps([asdict(d) for d in self.deals.values()], indent=2, default=str))

    @classmethod
    def load(cls, path=config.LEDGER_PATH) -> "Ledger":
        obj = cls()
        for row in json.loads(path.read_text()):
            obj.deals[row["deal_id"]] = DealLedger(**row)
        return obj
