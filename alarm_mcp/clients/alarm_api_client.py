# alarm_mcp/clients/alarm_api_client.py — Async HTTP client for the Alarm API Simulator service.

from __future__ import annotations

import os
from typing import Any

import httpx


_DEFAULT_BASE_URL = "http://localhost:8000"
_DEFAULT_TOKEN = "demo-token"
_DEFAULT_TIMEOUT_SECONDS = 30.0


class AlarmApiClient:
    """Thin async wrapper around httpx.AsyncClient for the Alarm API Simulator.

    One instance per MCP server process; reuse the connection pool across tool calls.
    Base URL and bearer token are read from env on first instantiation.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: float = _DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            timeout=timeout,
        )

    @property
    def base_url(self) -> str:
        return self._base_url

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        resp = await self._client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def post(self, path: str, *, json_body: dict[str, Any] | None = None) -> Any:
        resp = await self._client.post(path, json=json_body or {})
        resp.raise_for_status()
        return resp.json()

    # ----- Endpoints -----

    async def health(self) -> dict[str, str]:
        return await self.get("/health")

    async def search_assets(
        self, query: str, limit: int = 10, unit: str | None = None
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"query": query, "limit": limit}
        if unit is not None:
            params["unit"] = unit
        return await self.get("/assets/search", params=params)

    async def get_asset_metadata(self, asset_id: str) -> dict[str, Any]:
        return await self.get(f"/assets/{asset_id}/metadata")

    async def list_alarms(
        self,
        asset_id: str | None = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "start_time",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
            "sort_by": sort_by,
            "sort_order": sort_order,
        }
        if asset_id is not None:
            params["asset_id"] = asset_id
        return await self.get("/alarms", params=params)

    async def get_alarm(self, alarm_id: str) -> dict[str, Any]:
        return await self.get(f"/alarms/{alarm_id}")

    async def alarm_summary(self, req: dict[str, Any]) -> dict[str, Any]:
        return await self.post("/alarms/summary", json_body=req)

    async def alarm_trends(self, req: dict[str, Any]) -> dict[str, Any]:
        return await self.post("/alarms/trends", json_body=req)

    async def alarm_correlation(self, req: dict[str, Any]) -> dict[str, Any]:
        return await self.post("/alarms/correlation", json_body=req)

    async def flood_analysis(self, req: dict[str, Any]) -> dict[str, Any]:
        return await self.post("/alarms/flood-analysis", json_body=req)

    async def rationalization_candidates(self, req: dict[str, Any]) -> dict[str, Any]:
        return await self.post("/alarms/rationalization-candidates", json_body=req)

    async def priority_score(self, alarm_id: str) -> dict[str, Any]:
        return await self.post("/alarms/priority-score", json_body={"alarm_id": alarm_id})

    async def operator_actions(self, req: dict[str, Any]) -> dict[str, Any]:
        return await self.post("/recommendations/operator-actions", json_body=req)

    async def generate_calculation(
        self, calculation_type: str, filters: dict[str, str] | None = None
    ) -> dict[str, Any]:
        return await self.post(
            "/calculation-code/generate",
            json_body={"calculation_type": calculation_type, "filters": filters or {}},
        )

    async def execute_calculation(
        self, calculation_id: str, filters: dict[str, str] | None = None
    ) -> dict[str, Any]:
        return await self.post(
            "/calculation-code/execute",
            json_body={"calculation_id": calculation_id, "filters": filters or {}},
        )

    async def kpi_definitions(self) -> dict[str, Any]:
        return await self.get("/analytics/kpi-definitions")


# ----- Module-level singleton -----

_client: AlarmApiClient | None = None


def get_alarm_api_client() -> AlarmApiClient:
    """Return the process-wide AlarmApiClient, constructing it on first call."""
    global _client
    if _client is None:
        _client = AlarmApiClient(
            base_url=os.environ.get("ALARM_API_BASE_URL", _DEFAULT_BASE_URL),
            token=os.environ.get("ALARM_API_TOKEN", _DEFAULT_TOKEN),
        )
    return _client


async def close_alarm_api_client() -> None:
    """Close the singleton client. Call from server shutdown / tests."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None