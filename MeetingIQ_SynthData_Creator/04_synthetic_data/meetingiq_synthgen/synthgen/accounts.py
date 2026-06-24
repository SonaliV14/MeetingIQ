"""The Rapid7 scenario, encoded as data (from SCENARIO_RAPID7.md).

Hero accounts (A1/A5/A8) carry explicit committees for realism; the rest are
filled deterministically by the skeleton generator using the same role template.
"""
from __future__ import annotations

# ---- products Priya can sell (real Rapid7 portfolio) ----
PRODUCTS = [
    "Exposure Command Essentials", "Exposure Command Ultimate", "InsightVM",
    "Surface Command", "InsightIDR", "MDR", "InsightCloudSec",
    "InsightAppSec", "Metasploit", "Incident Command", "Intelligence Hub",
]

# ---- internal cast (the tenant's revenue team) ----
USERS = [
    {"name": "Priya Menon",  "role": "Enterprise AE",        "persona": "salesperson",   "email": "priya.menon@rapid7.example"},
    {"name": "Dev Sharma",   "role": "Sales Engineer",       "persona": "presales",      "email": "dev.sharma@rapid7.example"},
    {"name": "Lena Ortiz",   "role": "MDR Specialist",       "persona": "presales",      "email": "lena.ortiz@rapid7.example"},
    {"name": "Marcus Hale",  "role": "Sales Manager",        "persona": "sales_manager", "email": "marcus.hale@rapid7.example"},
    {"name": "Aisha Khan",   "role": "Pre-sales Lead",       "persona": "presales",      "email": "aisha.khan@rapid7.example"},
    {"name": "Tom Becker",   "role": "SDR",                  "persona": "salesperson",   "email": "tom.becker@rapid7.example"},
    {"name": "Ravi Nair",    "role": "Deal Desk",            "persona": "ops",           "email": "ravi.nair@rapid7.example"},
]

# corporate bands and the role template every committee fills
BANDS = ["IC", "Manager", "Director", "VP", "C-level"]
ROLE_TEMPLATE = [
    ("economic_buyer", "high"),
    ("champion", "high"),
    ("technical_evaluator", "medium"),
    ("technical_evaluator", "medium"),
    ("blocker", "medium"),
    ("influencer", "medium"),
]

# ---- the 10 accounts ----
# state: open_advancing | open_new | at_risk | closed_won | closed_lost | expansion | steady
ACCOUNTS = [
    {"code": "A1", "name": "Meridian Health Systems", "vertical": "Healthcare", "size": 2000,
     "products": ["Exposure Command Ultimate", "MDR"], "competitor": "Tenable", "state": "open_advancing",
     "colour": "green", "trajectory": "improving", "acv": 280000, "hero": True},
    {"code": "A2", "name": "Northwind Logistics", "vertical": "Transportation", "size": 8000,
     "products": ["InsightIDR", "InsightCloudSec"], "competitor": "Microsoft Sentinel", "state": "open_advancing",
     "colour": "green", "trajectory": "improving", "acv": 420000, "hero": False},
    {"code": "A3", "name": "Cobalt Pay", "vertical": "Fintech", "size": 1200,
     "products": ["Exposure Command Ultimate"], "competitor": "Wiz", "state": "open_new",
     "colour": "yellow", "trajectory": "flat", "acv": 190000, "hero": False},
    {"code": "A4", "name": "Larkspur Retail Group", "vertical": "Retail", "size": 12000,
     "products": ["Surface Command", "InsightVM"], "competitor": "Qualys", "state": "open_new",
     "colour": "yellow", "trajectory": "flat", "acv": 260000, "hero": False},
    {"code": "A5", "name": "Vantage Semiconductors", "vertical": "Manufacturing", "size": 15000,
     "products": ["Exposure Command Ultimate", "InsightAppSec"], "competitor": "Tenable", "state": "at_risk",
     "colour": "red", "trajectory": "declining", "acv": 510000, "hero": True},
    {"code": "A6", "name": "Aspen Digital", "vertical": "Tech SaaS", "size": 900,
     "products": ["MDR"], "competitor": "Arctic Wolf", "state": "at_risk",
     "colour": "red", "trajectory": "declining", "acv": 150000, "hero": False},
    {"code": "A7", "name": "Granite State Bank", "vertical": "Banking", "size": 5000,
     "products": ["InsightVM", "Exposure Command Essentials"], "competitor": "Qualys", "state": "closed_won",
     "colour": "green", "trajectory": "na", "acv": 360000, "hero": False},
    {"code": "A8", "name": "Helios Energy", "vertical": "Energy", "size": 7000,
     "products": ["Exposure Command Ultimate"], "competitor": "CrowdStrike", "state": "closed_lost",
     "colour": "grey", "trajectory": "na", "acv": 340000, "hero": True},
    {"code": "A9", "name": "Brightwave Media", "vertical": "Media", "size": 1500,
     "products": ["InsightCloudSec"], "competitor": None, "state": "expansion",
     "colour": "green", "trajectory": "improving", "acv": 120000, "hero": False},
    {"code": "A10", "name": "Pinnacle Insurance", "vertical": "Insurance", "size": 10000,
     "products": ["Intelligence Hub", "InsightIDR"], "competitor": "Recorded Future", "state": "steady",
     "colour": "blue", "trajectory": "flat", "acv": 95000, "hero": False},
]

# ---- hand-authored hero committees (realistic names/sentiment arcs) ----
HERO_COMMITTEES = {
    "A1": [
        {"name": "Dana Reyes", "title": "CISO", "band": "C-level", "role": "economic_buyer", "power": "high", "sentiment_arc": ["neutral", "neutral", "positive", "positive"]},
        {"name": "Sam Okafor", "title": "Director, Security Ops", "band": "Director", "role": "champion", "power": "high", "sentiment_arc": ["positive", "positive", "positive", "positive"]},
        {"name": "Joel Tan", "title": "SOC Manager", "band": "Manager", "role": "technical_evaluator", "power": "medium", "sentiment_arc": ["neutral", "neutral", "positive"]},
        {"name": "Grace Liu", "title": "Procurement Manager", "band": "Manager", "role": "blocker", "power": "medium", "sentiment_arc": ["neutral", "neutral"]},
        {"name": "Anil Patel", "title": "Director, Compliance", "band": "Director", "role": "influencer", "power": "medium", "sentiment_arc": ["neutral", "positive"]},
    ],
    "A5": [
        {"name": "Erik Vance", "title": "CISO", "band": "C-level", "role": "economic_buyer", "power": "high", "sentiment_arc": ["positive", "neutral", "negative", "negative"]},
        {"name": "Nadia Roy", "title": "Vulnerability Mgmt Lead", "band": "Manager", "role": "champion", "power": "medium", "sentiment_arc": ["positive", "positive", "neutral", "negative"]},
        {"name": "Tomas Ruiz", "title": "Director, Procurement", "band": "Director", "role": "blocker", "power": "high", "sentiment_arc": ["neutral", "negative", "negative"]},
        {"name": "Karen Webb", "title": "Finance Business Partner", "band": "Director", "role": "influencer", "power": "high", "sentiment_arc": ["neutral", "negative"]},
    ],
    "A8": [
        {"name": "Marco Bianchi", "title": "CISO", "band": "C-level", "role": "economic_buyer", "power": "high", "sentiment_arc": ["neutral", "neutral", "negative"]},
        {"name": "Lauren Cho", "title": "SecOps Lead", "band": "Manager", "role": "champion", "power": "medium", "sentiment_arc": ["positive", "neutral", "negative"]},
        {"name": "Greg Mason", "title": "SOC Analyst", "band": "IC", "role": "technical_evaluator", "power": "low", "sentiment_arc": ["neutral", "neutral"]},
    ],
}

# ---- signal taxonomy (planted, scored against the ledger) ----
SIGNAL_TYPES = [
    "pricing_objection", "technical_objection", "incumbent_loyalty", "competitor_mention",
    "budget_signal", "authority_signal", "need_signal", "timing_signal",
    "sentiment_shift", "commitment", "champion_change", "compliance_concern",
]

# meeting arc (type, default_recorded). The skeleton picks a slice by stage.
MEETING_ARC = [
    ("sdr_qualification", False),
    ("discovery", True),
    ("technical_demo", True),
    ("poc_kickoff", True),
    ("poc_checkin", False),
    ("poc_results_business_case", True),
    ("pricing_packaging", True),
    ("vendor_security_review", False),
    ("negotiation", True),
    ("close_or_loss_debrief", False),
]
