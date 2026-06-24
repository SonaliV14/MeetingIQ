# Scenario World — Rapid7 (Synthetic Data Design)

**Phase:** P4 · **Status:** design checkpoint (the build steps live in P6: `SYNTHETIC_DATA_BUILD.md`).
**Role of this file:** define *what exists* in the synthetic world — the selling org, accounts, people, deals, the time-ordered meeting series, the planted signals + hidden ground-truth ledger, and every source artifact to generate. The P6 build doc turns this into data; the generator must not invent structure that contradicts this file.
**Grounded in:** `CLIENT_RESEARCH.md` (Rapid7 facts) + `MASTER_PROJECT_DOC.md` §5.5 (synthetic-data approach) + `FEATURE_LIST.md` (the capabilities the world must exercise).

> **Everything below is synthetic.** Rapid7 and its real, public products are modelled for realism (Infoglen client; public company). **All prospect/customer companies and all people are fictional** — no real customer relationships are implied.

---

## 1. The premise (one paragraph)

The synthetic tenant is **Rapid7's revenue team**. The hero user is **Priya Menon, Enterprise Account Executive**, who sells the **Command Platform** (lead with Exposure Command + MDR) to mid-market and enterprise **CISOs**. Her deals run a multi-meeting arc over months, across Zoom/Meet calls, Gmail, Slack, Jira, Salesforce, and shared documents. The world contains a spread of deals — healthy, new, at-risk, won, lost, and an existing customer up for expansion — so that **every feature pillar has something real to act on**, and so the deal-risk *trajectory* and *commercial significance* stories have history to draw on.

**One tenant** (`tenant_id = rapid7-gtm`), multi-tenant-ready from day one.

---

## 2. The selling org (our tenant)

### 2.1 Products Priya can sell (real Rapid7 portfolio)
Command Platform umbrella, with these line items quoted on deals: **Exposure Command** (Essentials / Ultimate), **InsightVM** (Vulnerability Management), **Surface Command** (Attack Surface Mgmt), **InsightIDR** (SIEM), **MDR** (Managed Detection & Response), **InsightCloudSec** (Cloud Security), **InsightAppSec** (App Security), **Metasploit**, **Incident Command**, **Intelligence Hub** (Threat Intelligence). Packaging knobs: Essentials vs Ultimate tier; MDR as a managed service add-on; annual ACV.

### 2.2 The internal cast (drives the 3 personas + internal-team-performance pillar)
| Person | Role | Persona tier | Shows up in |
|---|---|---|---|
| **Priya Menon** | Enterprise AE (hero) | Salesperson | every deal; the AE dashboard |
| **Dev Sharma** | Sales Engineer (SE) | Pre-sales | demos, POCs, technical deep-dives |
| **Lena Ortiz** | MDR / Product Specialist | Pre-sales | MDR-attached deals |
| **Marcus Hale** | Sales Manager (Priya's manager) | Sales manager | end-of-day roll-ups, coaching, approvals |
| **Aisha Khan** | Pre-sales Lead | Pre-sales | POC success criteria, scoring |
| **Tom Becker** | SDR | Salesperson | early qualification calls |
| Ravi Nair | Deal-desk / Procurement liaison (internal) | — | pricing & order-form steps |

These names anchor **internal contribution scoring, coaching loops, peer/manager ratings, and expertise-based action-item assignment** (e.g. an MDR question auto-routes to Lena; a cloud-security question to Dev).

---

## 3. The accounts (Rapid7's prospects & customers)

**10 fictional accounts**, chosen to spread across verticals, competitors, products, and deal states — so the colour-coded calendar, trajectory, win/loss, expansion, and commercial-significance features all have material.

| # | Account (fictional) | Vertical | Size | Lead products | Displacing / competitor | Deal state | Calendar colour | Trajectory |
|---|---|---|---|---|---|---|---|---|
| A1 | **Meridian Health Systems** | Healthcare | 2,000 | Exposure Command + MDR | Tenable + lean SOC | Active opp, advancing | 🟢 Green | Improving |
| A2 | **Northwind Logistics** | Transport/Logistics | 8,000 | InsightIDR + InsightCloudSec | Microsoft Sentinel | Active opp, advancing | 🟢 Green | Improving |
| A3 | **Cobalt Pay** | Fintech | 1,200 | Exposure Command Ultimate | Wiz (cloud) + Qualys | New / discovery | 🟡 Yellow | Flat (early) |
| A4 | **Larkspur Retail Group** | Retail / e-comm | 12,000 | Surface Command + InsightVM | Qualys (incumbent) | New / discovery | 🟡 Yellow | Flat (early) |
| A5 | **Vantage Semiconductors** | Manufacturing | 15,000 | Exposure Command + InsightAppSec | Tenable (incumbent) | At-risk — budget freeze | 🔴 Red | Declining |
| A6 | **Aspen Digital** | Tech SaaS | 900 | MDR | Arctic Wolf (head-to-head) | At-risk — champion left | 🔴 Red | Declining |
| A7 | **Granite State Bank** | Banking | 5,000 | InsightVM + Exposure Command | (won vs Qualys) | Closed-won (recent) | 🟢 Green | n/a (post-sale) |
| A8 | **Helios Energy** | Energy / Utilities | 7,000 | Exposure Command | Lost to CrowdStrike | Closed-lost | ⚪ Grey/closed | n/a (loss review) |
| A9 | **Brightwave Media** | Media / Streaming | 1,500 | (customer) InsightIDR → +InsightCloudSec | — (expansion) | Existing customer, upsell | 🟢 Green | Improving |
| A10 | **Pinnacle Insurance** | Insurance | 10,000 | Intelligence Hub + InsightIDR | Recorded Future (intel) | Steady recurring touch | 🔵 Blue | Flat |

### 3.1 Buying-committee template (per account)
Each account carries a buying committee with **roles** (feeds stakeholder mapping, buying-committee heatmap, decision-power scoring):
- **Economic buyer** — CISO or VP Security.
- **Champion** — Director of Security Ops / VM lead (our internal advocate).
- **Technical evaluators** — SOC manager, cloud security lead, detection engineer.
- **Blocker** — Procurement, or an incumbent-tool loyalist.
- **Influencers** — CTO / VP Eng (cloud & app coverage), Compliance/GRC (audit, CMMC).

Each contact gets: name, title, **corporate band** (IC / Manager / Director / VP / C-level), **decision power** (low/med/high), email, and a sentiment-per-meeting series.

### 3.2 Three hero accounts (full detail — the demo golden path uses these)

**A1 · Meridian Health Systems — 🟢 improving, the "healthy deal" story**
- Opportunity: *Meridian — Exposure Command + MDR*, Stage **Technical Validation → Business Case**, ACV ~**$280k**, close target +6 weeks.
- Committee: **Dana Reyes** (CISO, C-level, high power, economic buyer, warming); **Sam Okafor** (Dir. SecOps, Director, high, **champion**, positive); **Joel Tan** (SOC Manager, Manager, med, technical, neutral→positive); **Pri%a's blocker** — **Grace Liu** (Procurement, Manager, med, process-driven); **Influencer** — **Dr. Patel** (Compliance, Director, med, cares about HIPAA/audit).
- Arc: discovery → demo → POC (InsightVM scan of a sample environment) → POC results → business case → (pending) pricing. Trajectory **improving** because POC found real exposures the incumbent missed.

**A5 · Vantage Semiconductors — 🔴 declining, the "at-risk deal" story**
- Opportunity: *Vantage — Exposure Command + InsightAppSec*, Stage **stalled in Negotiation**, ACV ~**$510k**, close slipping.
- Committee: **Erik Vance** (CISO, C-level, high, lukewarm); **Nadia Roy** (VM Lead, Manager, med, **champion but losing influence**); **Tomás Ruiz** (Procurement, Director, high, **blocker — budget freeze**); **Influencer** — **Karen Webb** (CFO's office, "not this quarter").
- Arc: strong start → competitor (Tenable incumbent) re-engaged → budget freeze signalled → champion went quiet. Trajectory **declining**; risk driven by budget + timing + cooling sentiment. This is the deal that should glow **red** and show a downward trajectory line.

**A8 · Helios Energy — ⚪ closed-lost, the "learn from the loss" story**
- Opportunity: *Helios — Exposure Command*, **Closed-Lost to CrowdStrike**, ACV was ~$340k.
- Loss reasons (ground truth): CrowdStrike incumbency on endpoint, a weak technical demo (internal performance gap), and a late executive sponsor. Feeds **loss analysis, internal coaching, and VoC**.

*(The other 7 accounts get compact profiles generated from the §3 table + committee template; full meeting scripting is LLM-expanded in P6.)*

---

## 4. The meeting series (deal arc)

### 4.1 Standard B2B-security sale arc (meeting types)
The generator draws each deal's meetings from this ordered template; stage determines how far along the arc a deal is.

1. **SDR qualification call** (Tom + prospect) — short, audio optional
2. **Discovery call** (Priya + prospect security lead) — *recorded*
3. **Technical deep-dive / demo** (Priya + Dev + SOC team) — *recorded*
4. **POC / trial kickoff** (Dev + prospect) — *recorded*
5. **POC check-in** ×1–2 (Dev + Aisha + prospect)
6. **POC results & business case** (Priya + champion + CISO) — *recorded*
7. **Pricing & packaging** (Priya + Procurement) — *recorded*
8. **Vendor security review** (prospect reviews Rapid7 itself) — Jira/doc-heavy
9. **Negotiation / redlines** (Priya + Procurement + Legal)
10. **Close / onboarding kickoff** (won deals) **or** **loss debrief** (lost deals, internal)

Plus **internal syncs**: deal war-room Slack threads, manager 1:1s (coaching), MDR specialist consults.

### 4.2 Counts (per master doc §5.5: 6–15 meetings per opportunity)
- Hero deals (A1, A5): **10–12 meetings** each across the arc.
- Active deals (A2, A3, A4, A9): **6–9 meetings** each.
- Closed deals (A7, A8): **8–10 meetings** (full history).
- Steady/blue (A10): **3–4 recurring** touches.
- Total: **~70–80 meetings** across the world.

### 4.3 Time anchoring
- The generator pins a fixed **`DEMO_TODAY` = a Monday in mid-June 2026** (e.g. 2026-06-08; the generator enforces the weekday).
- **History:** deals back-dated across **Feb–Jun 2026** so trajectories have ≥4 data points.
- **Future:** each open deal has **1–3 upcoming meetings** in the *next 2 weeks* after `DEMO_TODAY`, so the calendar/triage/pre-meeting-prep features have live material on "Monday morning."
- All dates are **offsets from `DEMO_TODAY`**, fixed seed → fully reproducible.

---

## 5. Planted signals & the hidden ground-truth ledger

The point of synthetic data: **plant signals on purpose**, then keep an answer key (the ledger) that evals score extraction/scoring against.

### 5.1 Signal taxonomy (aligned to the 9 risk families + BANT/MEDDICC)
| Signal type | Example planted line | Feeds |
|---|---|---|
| Pricing objection | "Ultimate is well above what we budgeted." | risk, objection extraction, BANT-Budget |
| Technical / integration objection | "We need this to feed our existing Splunk." | risk, objection extraction |
| Incumbent loyalty | "We've run Tenable for six years." | risk, competitor signal |
| Competitor mention | "CrowdStrike's already on every endpoint." | competitor signal, win/loss |
| Budget signal | "Budget's frozen until next fiscal year." | BANT-Budget, timing, risk |
| Authority signal | "I'll need the CFO's office to sign off." | BANT-Authority, decision-power |
| Need / pain signal | "We failed the last audit on patch SLAs." | BANT-Need, value framing |
| Timing signal | "We want this live before our SOC2 in Q4." | BANT-Timing, trajectory |
| Sentiment shift | champion warm → cool across meetings | sentiment, trajectory |
| Commitment / next-step | "I'll get you our asset inventory by Friday." | commitment tracker |
| Champion change | champion leaves the company (A6) | risk, stakeholder map |
| Compliance concern | HIPAA / CMMC / SOC2 requirements | need, doc RAG, persona |

### 5.2 Ground-truth ledger (the answer key) — schema per deal
Stored as a hidden JSON the product never sees; only evals read it.
```
deal_id, account, true_stage, true_risk_score (0–100), true_trajectory (improving|flat|declining),
bant_truth { budget, authority, need, timing : known|partial|unknown + evidence_meeting_id },
meddicc_truth { metrics, economic_buyer, decision_criteria, decision_process, paper_process, identify_pain, champion },
competitor, win_loss { outcome, reasons[] },                       # for closed deals
planted_signals[] { meeting_id, type, polarity(+/-/neutral), text_hint, expected_extraction },
commitments[] { meeting_id, owner, text, due_offset, fulfilled(bool) },
commercial_significance[] { meeting_id, true_value(low|med|high), created_opp(bool), advanced_opp(bool) },
committee_coverage_truth { role : engaged|absent|unknown }
```
The generator writes a ledger row for every deal **as it plants each signal** — so the truth is generated *with* the artifact, never reverse-engineered.

### 5.3 Worked example (A1 · Meridian, abbreviated)
- `true_trajectory: improving`; `true_risk_score: 28`.
- Planted: M2 discovery → *need* ("failed audit on patch SLAs"); M4 POC kickoff → *commitment* (Sam: "asset inventory by Friday", fulfilled=true); M6 POC results → *sentiment +* (CISO Dana warms); M7 pricing → *budget* objection (mild) + *timing* ("before HIPAA audit Q4").
- `bant_truth`: Budget=partial, Authority=known (Dana), Need=known, Timing=known.
- `commercial_significance`: M6 = high (advanced_opp), M2 = med (created_opp).

---

## 6. Sources to synthesise (every artifact, mapped to features)

The world is multi-source by design — that's the moat. Each deal generates artifacts across these sources, all emitted in the **canonical schema** via the ingestion-adapter contract.

| Source | What gets generated | Volume target (world) | Powers features |
|---|---|---|---|
| **Calendar** (Google) | Every meeting as an event (attendees, time, title) | ~70–80 events | triage workspace, colour matrix, pre-meeting prep |
| **Recorded call audio** | TTS-generated audio for selected meetings → Whisper STT transcripts | **10–12 audios** (across hero/active deals); rest are text transcripts | call intelligence, sentiment, signal extraction, summaries |
| **Email** (Gmail) | Intro, per-meeting recap, scheduling, procurement, "going quiet" threads | ~120–160 messages | follow-up automation, urgent-action safety net, commitment tracker |
| **Chat** (Slack) | Internal deal war-rooms (#deal-meridian…), AE↔SE coordination, manager 1:1s, MDR consults | ~10 channels, ~250 messages | cross-dept pane, internal team performance, intent routing |
| **Work tracking** (Jira) | POC setup tasks, vendor-security-review checklist, follow-up tasks | ~40 issues | action items, SLA escalation, failure recovery |
| **Documents** | Proposal/quote, competitive battlecard (per competitor), POC success-criteria doc, security-questionnaire response, MSA/order form, Rapid7 2026 threat report (leave-behind) | ~30 docs | document RAG, collateral engine, offering engine |
| **CRM rows** (Salesforce-shaped Postgres) | Account, Contact, Opportunity, Task, Event, Note — `external_id` null (Stage-3 slot) | 10 accounts · ~55 contacts · ~16 opps · tasks/events | 360 pack, field-update recos, approval gate, channel attribution |
| **External news** | A small fixture set of fresh "news" items per account/industry | ~20 items | news enrichment, talking points |
| **Firmographics** | Size/vertical/profile record per account (esp. net-new A3/A4) | 10 records | firmographic enrichment |

### 6.1 Which meetings get audio (the 10–12)
Pick the meetings where conversation signal concentrates, so call-intelligence has substance:
- A1: discovery, technical demo, POC results (3)
- A5: discovery, negotiation (the cooling one), a tense pricing call (3)
- A2: discovery, demo (2)
- A6: the MDR head-to-head call (1)
- A7: the winning business-case call (1)
- A8: the weak demo (the one that lost it) (1)
- A3: discovery (1)
→ **12 audios.** Each ~3–8 min of dialogue between 2–4 named speakers, with planted signals embedded in the script. TTS uses distinct voices per speaker; Whisper transcribes back (so the pipeline is exercised end-to-end, not faked).

---

## 7. The demo golden path ("Priya's Monday morning")

A scripted walk-through that touches every pillar, using the hero accounts:
1. **Land on the triage workspace** → week view, colour-coded. Meridian 🟢 (opportunity, count badge), two 🟡 new accounts, **Vantage 🔴**. (Pillars 1–2)
2. **Urgent-action safety net** flags an Aspen Digital follow-up that's gone quiet (champion left). (Pillar 2)
3. **Open Vantage (🔴)** → 360° command center → deal-risk **trajectory line trending down**, with the budget-freeze and competitor signals cited. (Pillars 1, 5, 7)
4. **Pre-meeting prep** for Meridian's upcoming business-case call → brief, committee with decision power, fresh HIPAA-related news, recommended offering, ready-made deck. (Pillar 3)
5. **Ask the copilot**: "What did Sam commit to and did it happen?" → cited answer from the commitment tracker. (Pillars 4, 7)
6. **End-of-day manager view** (Marcus): commercial significance of today's meetings, plus an **internal coaching** note from the weak Helios demo. (Pillars 5, 6)
7. **Executive roll-up**: VoC themes across the quarter + a one-click QBR pack. (Pillar 8)

---

## 8. Volume summary (targets for the generator)

| Entity | Target |
|---|---|
| Tenant | 1 (`rapid7-gtm`) |
| Internal users | 7 |
| Accounts | 10 |
| Contacts (buying-committee members) | ~55 |
| Opportunities | ~16 (1–3 per active/closed account) |
| Meetings (events) | ~70–80 |
| Recorded-call audios → Whisper transcripts | **12** |
| Text transcripts (no audio) | ~60 |
| Emails | ~120–160 |
| Slack channels / messages | ~10 / ~250 |
| Jira issues | ~40 |
| Documents | ~30 |
| News items | ~20 |
| Ground-truth ledger rows | 1 per deal (~16) |

---

## 9. What P5 and P6 take from here
- **P5 (env):** confirms the API keys these sources need — **TTS** (12 audios), **Whisper STT** (transcribe them), Gemini (later embedding), Anthropic (LLM expansion of transcripts/emails/docs + signal planting) — and the databases to land it all.
- **P6 (build):** turns §3–§6 into a deterministic skeleton (Polars + Faker, fixed seed) → LLM-expands each row into rich artifacts → generates audio → transcribes → validates against a JSON schema **and** the §5 ground-truth ledger.
- **P7 (mapping/load):** maps every canonical record to its real source shape (Salesforce objects, Gmail, Calendar, Slack, Jira) and loads the data so it's queryable before the context layer.
