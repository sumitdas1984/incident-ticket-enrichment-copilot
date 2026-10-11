# Current system status

## High-level status

The project is the **Incident & Ticket Enrichment Copilot** — an enterprise
AI assistant that helps service engineers investigate industrial alarms
and draft incident tickets. From the four planned runtime components
in `docs/01_project_overview.md`, **two are implemented and runnable**,
**two are placeholders**.

```
                 ┌────────────────────────────────────────────────────┐
                 │               Implemented & runnable               │
                 ├────────────────────────────────────────────────────┤
                 │ ✅ alarm_api/   — Alarm API Simulator service      │
                 │                   (FastAPI, 15 routes, layered)    │
                 │                                                    │
                 │ ✅ alarm_mcp/   — MCP server                       │
                 │                   (fastmcp, 9 tools, HTTP client)  │
                 ├────────────────────────────────────────────────────┤
                 │               Not yet implemented                  │
                 ├────────────────────────────────────────────────────┤
                 │ ❌ copilot/     — orchestration brain (planned)    │
                 │ ❌ frontend/    — chat UI (Streamlit/React/...)    │
                 ├────────────────────────────────────────────────────┤
                 │          Cross-cutting (missing everywhere)        │
                 ├────────────────────────────────────────────────────┤
                 │ ❌ RAG pipeline (chunking, embeddings, vector DB)  │
                 │ ❌ Document corpus                                │
                 │ ❌ Ticketing backends (Jira/SN/Azure/GitHub)       │
                 │ ❌ Docker / Docker Compose                        │
                 │ ❌ GitHub Actions CI                              │
                 │ ❌ tests/ directory (pytest config points to it)   │
                 └────────────────────────────────────────────────────┘
```

## What works today (verified in this session)

**`alarm_api/` — Alarm API Simulator service** (FastAPI, port 8000)
- 15 routes covering the full baseline `specs/alarm-api/Alarm-API-Simulator.postman_collection.json`:
  - assets: `/assets/search`, `/assets/{id}/metadata`
  - alarms: `/alarms`, `/alarms/{id}`, `/alarms/summary`, `/alarms/trends`,
    `/alarms/correlation`, `/alarms/flood-analysis`,
    `/alarms/rationalization-candidates`, `/alarms/priority-score`
  - recommendations: `/recommendations/operator-actions`
  - calculations: `/calculation-code/generate`, `/calculation-code/execute`
  - analytics: `/analytics/kpi-definitions`
  - system: `/health`, `/`
- Layered architecture: `models/` (Pydantic) → `data/` (seeds) →
  `repositories/` (in-memory) → `services/` (business logic) →
  `routes/` (FastAPI thin layer) → `main.py` (12 lines, just wires the router)
- Deterministic seed data: 12 assets, 20 alarms, 6 KPI definitions
- Live smoke test passed against `curl` for every route family

**`alarm_mcp/` — MCP server** (talks to `alarm_api` over HTTP, never imports it in-process)
- 9 tools: `search_assets`, `get_asset_metadata`, `list_alarms`, `get_alarm`,
  `alarm_summary`, `alarm_trends`, `alarm_correlation`, `priority_score`,
  `operator_actions`
- Built on `fastmcp` 2.x (not `mcp[cli]`), uses `httpx` async client
- Process-wide singleton `AlarmApiClient` (one `httpx.AsyncClient` per server)
- Verified end-to-end via `fastmcp call alarm_mcp/main.py <tool> args=...`

**Infrastructure that exists but isn't wired in:**
- `docs/01_project_overview.md` — full architecture doc
- `specs/alarm-api/` — 3 Postman collections (source of truth for the contract)
- `README.md` — quickstart + env-var config
- `pyproject.toml` — `fastapi`, `pydantic`, `uvicorn`, `fastmcp`, `httpx` deps
- `uv.lock` — locked dep tree
- `CLAUDE.md` — Claude Code instructions for the repo
- `.claude/settings.local.json` — restricted bash perms (`git rm *`, `uv sync *`, `uv run *`)
- `.gitignore` — covers `.venv/`, `.env`, `__pycache__`, mypy/ruff caches

## Pending work, ranked by impact

### Top priority — completes the planned runtime

1. **`copilot/` — orchestration brain.** FastAPI async service that:
   - Receives natural-language requests from the frontend
   - Plans the tool sequence
   - Invokes `alarm_mcp` tools (and RAG tools once they exist)
   - Combines results into a grounded response
   - Prepares a ticket draft for human approval before any write
   This is the heart of the project per the project-overview doc.

2. **`frontend/` — chat UI.** Streamlit/React/Gradio interface with:
   - Query input
   - Incident summary view
   - Document citations display
   - MCP execution trace
   - Editable ticket draft with explicit approve-before-create flow

### Medium priority — production hardening

3. **RAG pipeline + document corpus.** Chunking → embedding → vector store
   → semantic retrieval. Currently no documents exist; the contract calls
   for troubleshooting guides, operating procedures, knowledge articles,
   maintenance manuals, resolution notes, escalation procedures.
4. **Ticketing backends.** Pluggable adapters for Jira, ServiceNow,
   Azure DevOps, GitHub Issues, Mock. Currently none exist; the
   README says they're pluggable.
5. **Docker / Docker Compose.** Packaging for one-command bring-up.
6. **GitHub Actions CI.** Run ruff/mypy/pytest on every push.

### Lower priority — gap closure on what's already built

7. **`tests/` directory.** `pyproject.toml` already says `testpaths = ["tests"]`
   but the directory doesn't exist. The four chained Postman calls in
   `specs/alarm-api/chaining/` are a natural starting test surface.
8. **Auth enforcement in `alarm_api`.** `Authorization: Bearer ...` is
   sent by the Postman collection but ignored. Single `Depends(verify_token)`
   at the app level.
9. **`X-Correlation-Id` echo middleware.** Spec requires it; not implemented.
10. **Spec-conformant error envelope.** Replace FastAPI's default
    `{detail: [...]}` 422 with `{error: {code, message, correlation_id}}`
    via a single exception handler.
11. **Wheel packages list cleanup.** `pyproject.toml` still lists
    `copilot`, `mcp_server`, `simulator`, `frontend` as wheel packages
    that don't all exist on disk. The two duplicate names (`simulator`,
    `mcp_server`) should be dropped now that `alarm_api` and `alarm_mcp`
    exist.

## Recommended next step

The highest-leverage thing to plan next is either **(1) the `copilot/`
orchestration brain** (completes the runtime) or **(8) auth on
`alarm_api`** (closes the most-cited spec gap on what's already
shipping). Pick one and the next planning session will dive in.
