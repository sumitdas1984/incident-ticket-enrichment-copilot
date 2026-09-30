# Incident & Ticket Enrichment Copilot

An AI-powered assistant that helps service engineers investigate industrial alarms and prepare high-quality incident tickets. The Copilot automatically gathers alarm context, asset metadata, operator recommendations, similar historical cases, and relevant troubleshooting documentation, then assembles them into a reviewable incident draft — and never writes to a ticketing system without explicit user approval.

---

## Why it exists

When a high-priority industrial alarm fires, service engineers perform the same multi-step workflow manually across multiple disconnected systems: locate the affected asset, read the alarm, find similar historical incidents, look up the right procedure, check operator recommendations, then draft a ticket. The process is slow, repetitive, and error-prone under pressure.

This Copilot compresses that workflow into a single conversational request — and keeps a human in the loop before any ticket write.

---

## Highlights

- **MCP-native integration** — the LLM never talks to the Alarm Management API directly; it only invokes MCP tools with typed schemas, validation, retry, and trace propagation.
- **Document-grounded reasoning** — every response cites the procedures, knowledge articles, and historical resolution notes it was grounded in.
- **Multi-step orchestration** — asset resolution, alarm enrichment, recommendation lookup, similar-ticket search, and document retrieval are chained transparently with a visible execution trace.
- **Human-in-the-loop write operations** — tickets are drafted and previewed; nothing is created until the user explicitly approves.
- **Production-oriented architecture** — clean separation of UI, orchestration, MCP client/server, RAG pipeline, and persistence; environment-driven configuration; full test suite; Docker packaging.
- **Self-contained Alarm API simulator** — implements the same contract as a real industrial alarm system, so the entire stack runs locally with no external dependencies.

---

## Architecture

```
                   User
                     │
                     ▼
             Chat-Based Frontend
                     │
                     ▼
             Copilot Backend
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
      MCP Client          RAG Retrieval
          │                     │
          ▼                     ▼
      MCP Server         Vector Database
          │                     │
          ▼                     ▼
 Alarm API Simulator     Document Corpus
          │                     │
          └──────────┬──────────┘
                     ▼
          AI Grounded Response
                     │
                     ▼
 Incident Summary + Citations +
 Ticket Draft + MCP Execution Trace
```

See [`docs/01_project_overview.md`](docs/01_project_overview.md) for the full system description.

---

## Tech stack

| Layer | Technology |
| --- | --- |
| Copilot backend | Python, FastAPI, async I/O |
| MCP server | Python MCP SDK |
| MCP client | Python MCP SDK |
| RAG pipeline | Embeddings + vector store |
| Alarm API simulator | FastAPI |
| Ticketing | Pluggable — Jira / ServiceNow / Azure DevOps / GitHub Issues / Mock |
| Frontend | React / Streamlit / Gradio |
| Packaging | Docker, Docker Compose |
| CI | GitHub Actions |
| Tests | pytest |

---

## Quickstart

> The codebase is under active development. The following flow is the target once the first release is tagged.

```bash
# 1. Clone
git clone https://github.com/<org>/incident-ticket-enrichment-copilot.git
cd incident-ticket-enrichment-copilot

# 2. Configure
cp .env.example .env
# edit .env with your API keys, simulator URL, etc.

# 3. Run the full stack
docker compose up --build

# 4. Open the UI
# http://localhost:8501   (Streamlit default)
```

For local development without Docker:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Terminal 1 — Alarm API simulator
uvicorn simulator.main:app --reload --port 8000

# Terminal 2 — MCP server
python -m mcp_server

# Terminal 3 — Copilot backend
uvicorn copilot.main:app --reload --port 8080

# Terminal 4 — Frontend
streamlit run frontend/app.py
```

---

## Configuration

All configuration is environment-driven. See `.env.example` for the full list. Key variables:

- `ALARM_API_BASE_URL` — URL of the Alarm API simulator
- `ALARM_API_TOKEN` — auth token for the simulator
- `LLM_API_KEY` — provider API key
- `LLM_MODEL` — model identifier
- `RAG_INDEX_PATH` — path to the persisted vector index
- `TICKETING_BACKEND` — `jira` | `servicenow` | `azure_devops` | `github` | `mock`

Secrets must never be committed; `.env` is git-ignored.

---

## Development

```bash
# Run the test suite
pytest

# With coverage
pytest --cov=. --cov-report=html

# Lint / type-check
ruff check .
mypy .
```

---

## Documentation

- [`docs/01_project_overview.md`](docs/01_project_overview.md) — system architecture and components
- `docs/02_mcp_tool_catalog.md` — MCP tool reference *(coming with the first MCP server)*
- `docs/03_rag_design.md` — RAG ingestion and retrieval design *(coming with the first RAG pipeline)*
- [`specs/alarm-api/`](specs/alarm-api/) — Alarm API specification (Postman collections serving as the executable contract)

---

## Project status

This project is under active development. The first tagged release will include:

- Alarm API simulator honouring the [`specs/alarm-api/`](specs/alarm-api/) contract
- MCP server exposing alarm and ticketing tools
- MCP client integration in the Copilot backend
- RAG pipeline over a curated document corpus
- Chat-based frontend with MCP execution trace and citations
- Docker Compose packaging and CI

---

## License

TBD — to be selected before first public release.
