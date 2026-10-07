# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project shape

A production-oriented enterprise AI Copilot that helps service engineers investigate industrial alarms and prepare incident tickets. The architecture has four planned runtime components — **Copilot backend** (FastAPI async), **MCP server**, **Alarm API simulator**, **chat frontend** — wired together via Docker Compose. The full architecture and end-to-end flow are described in `docs/01_project_overview.md`. The README has the Quickstart and configuration knobs (`ALARM_API_BASE_URL`, `ALARM_API_TOKEN`, `LLM_API_KEY`, `LLM_MODEL`, `RAG_INDEX_PATH`, `TICKETING_BACKEND`).

Only the **Alarm API simulator** is implemented today. The other three components (`copilot/`, `mcp_server/`, `frontend/`) are placeholders declared in `pyproject.toml`'s `[tool.hatch.build.targets.wheel] packages = [...]` but do not yet exist on disk.

## The Alarm API contract

`specs/alarm-api/` is the **source of truth** for the Alarm API. The three Postman collections (`Alarm-API-Simulator`, `scenarios/`, `chaining/`) define every endpoint, request/response schema, `Authorization` header, `X-Correlation-Id` echo, pagination convention, and multi-step chaining flow that the simulator MUST honour. Per the spec README:

> When adding a new endpoint or changing an existing one: update the relevant collection(s) here **first**, then implement the change in the simulator.

Auth header is `Authorization: Bearer {{token}}` (currently unvalidated — see "Known gaps" below). List endpoints paginate with `{items, page, page_size, total}`; search endpoints use `{results: [...]}`. Errors must conform to `{error: {code, message, correlation_id}}` (also currently unhandled — see below). Validate the simulator against the collections with `newman run`.

## `alarm_api/` layered package layout

The simulator is split into a clean 3-layer architecture (routes → services → repositories). Read these top-down — `main.py` is 12 lines and just wires the router.

```
alarm_api/
├── main.py                    # FastAPI app + include_router — nothing else
├── models/                    # Pydantic schemas, one module per resource family (asset, alarm, recommendation, calculation, kpi, common)
├── data/                      # Deterministic seed lists (assets.py, alarms.py, kpis.py)
├── repositories/              # In-memory data access; module-level singletons
├── services/                  # Business logic; classes take repos via constructor
└── routes/                    # FastAPI APIRouters; thin HTTP layer
```

**Conventions to preserve:**

- Routes depend on services via `Annotated[ServiceT, Depends(get_service)]` — the `service` parameter must come **before** any `Query`/`Path` parameter with a default, otherwise Python raises `SyntaxError: parameter without a default follows parameter with a default`.
- Service factories (`get_asset_service`, `get_alarm_service`, `get_recommendation_service`, `get_calculation_service`) take their repository/service dependencies through `Annotated[..., Depends(...)]` too. The default-value form (`repo: AlarmRepository = get_alarm_repository()`) breaks FastAPI's introspection — it interprets the callable as a request body field.
- Repositories are **module-level instances** in `repositories/__init__.py` wired to the seed. Services are constructed per request via `Depends()`. Don't try to make services singletons — they hold no state worth sharing.
- Don't name a method `list` — it shadows the builtin inside class-body annotations (`list[str]` in a subsequent method's signature throws `'function' object is not subscriptable`). Existing code uses `paginated_list` and `paginated` for this reason.
- `models/__init__.py` and `data/__init__.py` re-export everything so `from alarm_api.models import Asset` and `from alarm_api.data import ALARMS` keep working — keep that re-export surface when splitting or adding modules.
- Routes must not import repositories directly. The analytics route is the one exception (`routes/analytics.py` calls `KpiRepository` directly), but the rest go through services.

## Commands

```bash
# Install deps (project uses uv; pyproject.toml is the manifest)
uv sync --extra dev

# Run the simulator
uv run uvicorn alarm_api.main:app --reload --port 8000

# Tests (note: no tests/ directory exists yet — pytest reports 0 collected)
uv run pytest
uv run pytest --cov=. --cov-report=html
uv run pytest tests/test_foo.py::test_bar   # single test

# Lint / format
uv run ruff check .
uv run ruff check . --fix
uv run ruff format .

# Type-check (mypy strict is on)
uv run mypy alarm_api
```

**Bash permission scope** in `.claude/settings.local.json` is restricted to `git rm *`, `uv sync *`, `uv run *`. Anything else will prompt for approval — including `uv add`, file deletion, and Docker.

## Known gaps (follow-up work, not bugs)

- **Auth not enforced.** No `Depends(verify_token)` anywhere — every endpoint is reachable anonymously. `Authorization: Bearer ...` is in the Postman collection but the simulator ignores it.
- **Correlation id not echoed.** No middleware that reads `X-Correlation-Id` and reflects it on the response.
- **Error envelope mismatch.** FastAPI's default 422 returns `{detail: [...]}`, not the spec's `{error: {code, message, correlation_id}}`. No `app.exception_handler(RequestValidationError)` is registered.
- **`pyproject.toml` wheel packages mismatch.** `packages = ["copilot", "mcp_server", "simulator", "frontend"]` but only `alarm_api/` exists on disk. `uvicorn alarm_api.main:app` works via filesystem layout, not the wheel declaration.
- **No `tests/` directory.** `testpaths = ["tests"]` is set but nothing exists there. When adding them, follow the layered naming: `tests/test_alarm_api.py` or per-module `tests/test_services_alarm.py`.

## Spec change protocol

Any new endpoint or schema change to the Alarm API:

1. Update `specs/alarm-api/*.postman_collection.json` first.
2. Add the model in `alarm_api/models/<domain>.py` and re-export from `models/__init__.py`.
3. Add seed data if needed in `alarm_api/data/<domain>.py` and re-export from `data/__init__.py`.
4. Add repository methods (read-only first; mutate only when needed).
5. Add a service class + `get_*_service` factory.
7. Wire into a route module under `alarm_api/routes/<domain>.py` and include it from `routes/__init__.py`.
7. Validate with the affected Postman collection via `newman run`.