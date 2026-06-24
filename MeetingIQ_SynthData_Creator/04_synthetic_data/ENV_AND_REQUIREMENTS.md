# P5 — Environment, Tooling & Requirements (Windows 11)

**Scope:** everything needed to *create the synthetic data* on a Windows 11 laptop and load it into the first data stores. The heavier context-layer stores (Neo4j, vector DB, Elasticsearch) are **not** needed yet — they belong to the embedding/graph/chunking phase that comes after plain data creation.

---

## 1. The Rust / Polars question (answered first)

You do **not** need to install Rust to use Polars. Polars ships pre-compiled Python **wheels** (the Rust engine is inside the wheel); `pip install polars` just works on Windows 11. So:

- **Recommended path (what this package uses):** Python + `pip install polars`. No Rust toolchain, no compiler. Done.
- **Install Rust only if** you later want to (a) write native Rust, (b) use `polars` compiled from source, or (c) build the optional fast components. Then install via **rustup**: download `rustup-init.exe` from rustup.rs, run it, pick the default MSVC toolchain (it will prompt to install the *Visual Studio C++ Build Tools* — accept). Verify: `rustc --version`, `cargo --version`.
- **CPU note:** if you ever want the very fastest Polars on your specific CPU, install the optimized wheel: `pip install polars-lts-cpu` is the *safe* build for older CPUs; plain `polars` is fine for an i7.

> Bottom line for this project: `pip install polars` — that's the whole "Rust/Polars" requirement for synthetic-data creation.

---

## 2. Base toolchain

| Tool | Why | Install on Win 11 |
|---|---|---|
| **Python 3.11+** | the generator runs on it | python.org installer, or `winget install Python.Python.3.12` |
| **uv** (recommended) | fast venv + installs | `pip install uv` then `uv venv` / `uv pip install -r requirements.txt` |
| **Git** | version control | `winget install Git.Git` |
| **Docker Desktop + WSL2** | runs Postgres + MinIO | `winget install Docker.DockerDesktop`; enable WSL2 backend |
| **ffmpeg** | audio concat for TTS (Stage 3) and Whisper | `winget install Gyan.FFmpeg` (must be on PATH) |
| **VS Code** | editor; speaks MCP later | `winget install Microsoft.VisualStudioCode` |
| Node 20+ | only later (Next.js UI) | `winget install OpenJS.NodeJS.LTS` |

Setup in one go:
```powershell
winget install Python.Python.3.12 Git.Git Docker.DockerDesktop Gyan.FFmpeg Microsoft.VisualStudioCode
pip install uv
cd meetingiq_synthgen
uv venv && .venv\Scripts\activate
uv pip install -r requirements.txt
```

---

## 3. Databases — what's needed *now* vs *later*

For **plain synthetic-data creation + load** (this phase), only two stores are needed, both from the bundled `docker-compose.yml`:

| Store | Role now | Start |
|---|---|---|
| **Postgres 16** | Salesforce-shaped relational landing zone (accounts, contacts, opps, meetings, transcripts, tasks, emails, docs) | `docker compose up -d postgres` |
| **MinIO** | object storage for blobs — the 12 call audios + document files | `docker compose up -d minio` |

**Deferred to the context layer (commented in `docker-compose.yml`, do not start yet):** Neo4j (graph), Qdrant/Chroma (vectors), Redis (cache/memory), Elasticsearch/OpenSearch (BM25). These only matter once we embed, build nodes/edges, and chunk — explicitly out of scope for plain data creation.

---

## 4. API keys & services (only for the stages you run)

| Stage | Service | Key / setup | Cost at POC volume |
|---|---|---|---|
| 2 — LLM expansion | **Anthropic** (Claude) | `ANTHROPIC_API_KEY` | pennies–low $ (≈130 transcripts + ~120 emails + 30 docs on Sonnet) |
| 3 — TTS (12 calls) | **one of:** OpenAI TTS / Azure Speech / ElevenLabs / **pyttsx3 (offline, free)** | provider key, or none for pyttsx3 | a few cents for 12 short clips; free offline |
| 4 — Whisper STT | **local faster-whisper (no key)** *or* OpenAI Whisper API | none (downloads model once) / `OPENAI_API_KEY` | free locally |
| later — embeddings | Gemini Embedding 2 | `GOOGLE_API_KEY` | not needed for plain data |

**Recommended cheapest credible setup:** Anthropic for expansion, **OpenAI TTS** for natural multi-voice calls (or pyttsx3 if you want zero spend), **local faster-whisper** for transcription (no key, runs on the i7). Total spend to build the whole world: roughly a dollar or two.

Put keys in `.env` (copy from `.env.example`). Stage 1 (skeleton), Stage 5 (assemble), validate, and map need **no keys at all** — you can build and inspect the entire structural world offline first.

---

## 5. Sanity check (do this before anything else)
```powershell
python run.py skeleton     # offline, deterministic
python run.py validate     # expect: RESULT: PASS
python run.py map          # offline; writes Salesforce/Gmail/Slack/Jira archives
```
If those three pass, your Python environment is correct and you can layer in the keyed stages (`expand`, `tts`, `transcribe`) and the Docker load when ready. Full step-by-step with expected output per step: `SYNTHETIC_DATA_BUILD.md`.
