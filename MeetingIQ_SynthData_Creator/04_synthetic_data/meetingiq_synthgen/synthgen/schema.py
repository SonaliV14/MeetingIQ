"""Canonical entity models. Every source artifact normalises into these shapes
(the ingestion-adapter contract). `external_id` is the Salesforce-shaped slot,
null in the POC and filled at Stage-3 bridge time.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class Base(BaseModel):
    id: str
    tenant_id: str = "rapid7-gtm"
    external_id: Optional[str] = None     # SF id, null in POC
    source: str                           # crm | gmail | gcal | slack | jira | call | doc | news
    source_uri: Optional[str] = None
    timestamp: Optional[datetime] = None
    confidence: float = 1.0
    freshness: Optional[datetime] = None


class User(Base):
    name: str
    role: str
    persona: str
    email: str


class Account(Base):
    code: str
    name: str
    vertical: str
    size: int
    colour: str
    state: str


class Firmographic(Base):
    account_id: str
    vertical: str
    employee_band: str
    region: str
    profile: str


class Contact(Base):
    account_id: str
    name: str
    title: str
    band: str
    committee_role: str       # economic_buyer | champion | technical_evaluator | blocker | influencer
    decision_power: str       # low | medium | high
    email: str


class Opportunity(Base):
    account_id: str
    name: str
    stage: str
    products: list[str]
    acv: int
    owner_user_id: str
    close_date: Optional[datetime] = None
    is_closed: bool = False
    is_won: bool = False


class Meeting(Base):
    account_id: str
    opportunity_id: Optional[str]
    title: str
    meeting_type: str
    channel: str              # zoom | gmeet | internal
    attendee_user_ids: list[str]
    attendee_contact_ids: list[str]
    recorded: bool = False
    start: datetime
    duration_min: int = 30


class Transcript(Base):
    meeting_id: str
    text: str
    origin: Literal["text", "whisper"] = "text"


class Email(Base):
    thread_id: str
    account_id: str
    subject: str
    from_addr: str
    to_addrs: list[str]
    body: str


class ChatMessage(Base):
    channel_name: str
    account_id: Optional[str]
    author: str
    body: str


class ActionItem(Base):
    account_id: str
    meeting_id: Optional[str]
    title: str
    owner: str
    status: str = "open"      # open | done | overdue
    due: Optional[datetime] = None


class Document(Base):
    account_id: Optional[str]
    doc_type: str             # proposal | battlecard | poc_criteria | security_questionnaire | order_form | report
    title: str
    body: str


class NewsItem(Base):
    account_id: str
    headline: str
    body: str


class Signal(Base):
    deal_id: str
    meeting_id: Optional[str]
    signal_type: str
    polarity: str             # + | - | neutral
    text_hint: str
