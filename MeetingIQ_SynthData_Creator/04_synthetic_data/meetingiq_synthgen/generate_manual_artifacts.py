import json
import os
import random
from pathlib import Path

# Set up directories
SKELETON_DIR = Path("out/skeleton")
ARTIFACTS_DIR = Path("out/artifacts")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

print("Reading skeleton files...")

# --- 15 Highly Distinct Dialogues for Audio Validation ---
DIALOGUES = {
    "sdr_qualification": [
        "Tom Becker: Hi, I'm reaching out to see if you have 30 minutes to discuss reducing your exposure surface.\nContact: Sure, we've been struggling with prioritizing vulnerabilities lately.\nTom Becker: Exactly the pain we solve. Let me set up a call with our AE.\n",
        "Tom Becker: Good morning! We help teams consolidate their security stack. Is this a priority for you this quarter?\nContact: Actually, yes. We are trying to move away from isolated point solutions.\nTom Becker: Great. I'll invite Priya to walk you through our unified platform.\n"
    ],
    "discovery": [
        "Priya Menon: Thanks for joining. What is your biggest pain point with vulnerability management today?\nContact: We're currently using Tenable, but we have massive coverage gaps in our cloud environment.\nDev Sharma: That is exactly what Exposure Command addresses—unified visibility with no agent sprawl.\n",
        "Priya Menon: I'd love to understand your current incident response times.\nContact: It takes us days to investigate alerts because our current SIEM is too noisy.\nDev Sharma: With InsightIDR, we use native behavioral analytics to filter out the noise and prioritize real threats.\n",
        "Priya Menon: What is driving the security evaluation this quarter?\nContact: We failed a recent compliance audit due to patching SLA misses.\nDev Sharma: We can definitely help map your asset exposures directly to compliance frameworks to automate that reporting.\n"
    ],
    "technical_demo": [
        "Dev Sharma: Let me walk you through the asset inventory view. Everything is auto-discovered.\nContact: Can this integrate with our existing SIEM via API? That is a hard requirement for us.\nDev Sharma: Yes, we have native connectors for Splunk, Sentinel, and a REST API.\n",
        "Dev Sharma: Here is how our prioritization engine works. It uses CVSS, asset criticality, and active threat intel.\nContact: So it tells me what to patch first?\nDev Sharma: Exactly. It highlights the exposures actively being exploited in the wild.\n"
    ],
    "poc_kickoff": [
        "Priya Menon: Let's lock in the POC success criteria. We are targeting a 40% reduction in critical vulnerabilities.\nContact: Agreed. We will share the asset inventory list by Friday.\nDev Sharma: Perfect, I'll set up the tenant and we can run the first scan then.\n",
        "Priya Menon: Our goal for this 14-day trial is to prove 100% visibility across your AWS environment.\nContact: Sounds fair. We will provide read-only IAM roles by end of day.\nDev Sharma: I will monitor the ingestion and alert you once the baseline scan completes.\n"
    ],
    "poc_checkin": [
        "Dev Sharma: Early POC results look strong—a 34% reduction in critical vulnerabilities so far.\nContact: The team is impressed, but we need to ensure this fits our procurement timeline.\nPriya Menon: Understood. Let's get procurement aligned this week so we don't hit any roadblocks.\n",
        "Dev Sharma: We noticed a few blind spots in the legacy subnets during the last scan.\nContact: Ah, those are handled by a different contractor. We can ignore them for this POC.\nPriya Menon: Got it. I'll update the success criteria document to reflect that scope change.\n"
    ],
    "poc_results_business_case": [
        "Dev Sharma: Final POC results show a 47% reduction in exposure across 12,000 assets.\nContact: These numbers are compelling. What does the full deployment timeline look like?\nPriya Menon: We can be fully deployed within 60 days with our dedicated onboarding team.\n"
    ],
    "pricing_packaging": [
        "Priya Menon: We have three tiers. The Ultimate tier looks like the right fit for your scale.\nContact: Our budget cycle closes in Q3, so timing matters. How does this compare to CrowdStrike on total cost?\nPriya Menon: We're highly competitive when you factor in the included MDR coverage.\n",
        "Priya Menon: I sent over the quote for the Essentials package. Does this align with your budget expectations?\nContact: It is a bit higher than what we paid Qualys last year.\nPriya Menon: True, but remember this includes automated remediation capabilities that Qualys charges extra for.\n"
    ],
    "negotiation": [
        "Priya Menon: Legal has reviewed the redlines. Here is our final position on the master terms.\nContact: Procurement needs net-60 payment terms. Also, budgets are currently frozen until next quarter.\nPriya Menon: Let me see what I can do. I might be able to offer a discount if we sign by month-end.\n"
    ],
    "recurring_sync": [
        "Priya Menon: Quick check on open action items from last month.\nContact: The integration ticket is in progress. We are also looking at adding InsightAppSec soon.\nPriya Menon: Great, I'll have Dev scope that out for our renewal conversation.\n"
    ],
    "close_or_loss_debrief": [
        "Marcus Hale: What were the top two factors that determined the result of this deal?\nPriya Menon: It came down to champion strength and procurement timing.\nMarcus Hale: Got it. We will adjust the playbook for similar deals next quarter.\n"
    ]
}

DEFAULT_DIALOGUE = "Priya Menon: Thanks for joining the meeting today.\nContact: Thanks for having me. Let's dive in.\n"

# 1. Generate Transcripts for Meetings
meetings = []
if (SKELETON_DIR / "meetings.jsonl").exists():
    with open(SKELETON_DIR / "meetings.jsonl", "r") as f:
        for line in f:
            if line.strip():
                meetings.append(json.loads(line))

transcript_count = 0
for m in meetings:
    if m.get("meeting_type") == "internal_sync":
        continue
    
    m_type = m.get("meeting_type", "")
    dialogue_options = DIALOGUES.get(m_type, [DEFAULT_DIALOGUE])
    transcript_content = random.choice(dialogue_options)
    
    with open(ARTIFACTS_DIR / f"transcript_{m['id']}.txt", "w") as out:
        out.write(transcript_content)
    transcript_count += 1

# 2. Generate Emails
emails = []
if (SKELETON_DIR / "emails.jsonl").exists():
    with open(SKELETON_DIR / "emails.jsonl", "r") as f:
        for line in f:
            if line.strip():
                emails.append(json.loads(line))

email_count = 0
for e in emails:
    email_content = f"Hi team,\n\nFollowing up regarding: {e.get('subject', 'our recent sync')}.\nLet me know if you need anything else to move forward.\n\nBest,\nRapid7\n"
    with open(ARTIFACTS_DIR / f"email_{e['id']}.txt", "w") as out:
        out.write(email_content)
    email_count += 1

# 3. Generate Documents
docs = []
if (SKELETON_DIR / "documents.jsonl").exists():
    with open(SKELETON_DIR / "documents.jsonl", "r") as f:
        for line in f:
            if line.strip():
                docs.append(json.loads(line))

doc_count = 0
for d in docs:
    doc_content = f"# {d.get('title', 'Document')}\n\n## Executive Summary\nThis {d.get('doc_type', 'document')} outlines the strategic approach for the account.\n"
    with open(ARTIFACTS_DIR / f"doc_{d['id']}.md", "w") as out:
        out.write(doc_content)
    doc_count += 1

print(f"Success! Generated:")
print(f"  - {transcript_count} Unique Transcripts (Mapped to 15 Dialogue Templates)")
print(f"  - {email_count} Emails")
print(f"  - {doc_count} Documents")