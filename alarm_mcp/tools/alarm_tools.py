# alarm_mcp/tools/alarm_tools.py — MCP tool definitions that wrap the Alarm API Simulator.

from __future__ import annotations

from fastmcp import FastMCP

from alarm_mcp.clients.alarm_api_client import get_alarm_api_client


mcp = FastMCP("alarm-mcp")


# ----- Asset tools -----


@mcp.tool
async def search_assets(query: str, limit: int = 10, unit: str | None = None) -> dict:
    """Search the asset registry by name substring (case-insensitive).

    `query` is matched against the asset's human-readable `name` field. Optional
    `unit` filters to assets belonging to a specific process unit (e.g. 'Unit 5').
    Returns up to `limit` matches (1-100, default 10) in deterministic order.

    Typical chain step: identify the `asset_id` for a free-text asset name before
    calling `get_asset_metadata`, `list_alarms`, or `operator_actions`.
    """
    client = get_alarm_api_client()
    return await client.search_assets(query=query, limit=limit, unit=unit)


@mcp.tool
async def get_asset_metadata(asset_id: str) -> dict:
    """Return the full asset record (name, unit, site, asset_type) for `asset_id`.

    Raises an upstream 404 if the asset is unknown — surface the error to the LLM
    so it can adjust its asset_id.
    """
    client = get_alarm_api_client()
    return await client.get_asset_metadata(asset_id=asset_id)


# ----- Alarm tools -----


@mcp.tool
async def list_alarms(
    asset_id: str | None = None,
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "start_time",
    sort_order: str = "desc",
) -> dict:
    """List alarms with optional filtering by `asset_id` and basic pagination.

    `sort_by` accepts `start_time`, `priority`, or `alarm_id`. `sort_order` is
    `asc` or `desc`. Returns a paginated envelope `{data, page, page_size, total}`.
    """
    client = get_alarm_api_client()
    return await client.list_alarms(
        asset_id=asset_id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@mcp.tool
async def get_alarm(alarm_id: str) -> dict:
    """Return a single alarm record by ID, or 404 if unknown."""
    client = get_alarm_api_client()
    return await client.get_alarm(alarm_id=alarm_id)


@mcp.tool
async def alarm_summary(
    asset_ids: list[str] | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    severity: list[str] | None = None,
    group_by: list[str] | None = None,
    kpis: list[str] | None = None,
) -> dict:
    """Group filtered alarms and compute the requested KPIs.

    Filters: `asset_ids` (list), `start_time`/`end_time` (ISO-8601 strings), `severity`
    (subset of `low|medium|high|critical`). `group_by` defaults to `['alarm_name']`.
    `kpis` defaults to `['alarm_count']`; supported: `alarm_count`, `recurring_rate`,
    `avg_ack_delay_seconds`.
    """
    client = get_alarm_api_client()
    time_range = (
        {"start_time": start_time, "end_time": end_time}
        if start_time is not None and end_time is not None
        else None
    )
    req = {
        "asset_ids": asset_ids,
        "time_range": time_range,
        "severity": severity,
        "group_by": group_by if group_by is not None else ["alarm_name"],
        "kpis": kpis if kpis is not None else ["alarm_count"],
    }
    return await client.alarm_summary(req)


@mcp.tool
async def alarm_trends(
    asset_ids: list[str] | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    bucket: str = "daily",
    metrics: list[str] | None = None,
) -> dict:
    """Bucket filtered alarms by time and compute per-bucket metrics.

    `bucket` is `hourly` | `daily` | `weekly`. `metrics` defaults to `['alarm_count']`.
    """
    client = get_alarm_api_client()
    time_range = (
        {"start_time": start_time, "end_time": end_time}
        if start_time is not None and end_time is not None
        else None
    )
    req = {
        "asset_ids": asset_ids,
        "time_range": time_range,
        "bucket": bucket,
        "metrics": metrics if metrics is not None else ["alarm_count"],
    }
    return await client.alarm_trends(req)


@mcp.tool
async def alarm_correlation(
    asset_ids: list[str] | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    lag_window_minutes: int = 15,
    severity_threshold: str = "medium",
    min_support: int = 1,
) -> dict:
    """Find pairs of distinct alarm_names that activate within `lag_window_minutes`.

    `severity_threshold` is the minimum severity (inclusive) to include.
    `min_support` filters out rare co-occurrences.
    """
    client = get_alarm_api_client()
    time_range = (
        {"start_time": start_time, "end_time": end_time}
        if start_time is not None and end_time is not None
        else None
    )
    req = {
        "asset_ids": asset_ids,
        "time_range": time_range,
        "correlation_method": "cooccurrence",
        "lag_window_minutes": lag_window_minutes,
        "severity_threshold": severity_threshold,
        "min_support": min_support,
    }
    return await client.alarm_correlation(req)


@mcp.tool
async def priority_score(alarm_id: str) -> dict:
    """Compute a simple priority score for `alarm_id` (combines severity, age, ack state).

    Returns the score, the priority band (`low|medium|high|critical`), and a
    `factors` dict showing the components that produced the score.
    """
    client = get_alarm_api_client()
    return await client.priority_score(alarm_id=alarm_id)


# ----- Recommendation tools -----


@mcp.tool
async def operator_actions(
    alarm_id: str,
    include_related: bool = True,
    include_asset_context: bool = True,
    include_historical_pattern: bool = True,
) -> dict:
    """Return a deterministic set of operator-action recommendations for `alarm_id`.

    The response also includes related alarms, asset context, and the historical
    pattern for the alarm name — toggle each with the `include_*` flags.
    """
    client = get_alarm_api_client()
    req = {
        "alarm_id": alarm_id,
        "include_related": include_related,
        "include_asset_context": include_asset_context,
        "include_historical_pattern": include_historical_pattern,
    }
    return await client.operator_actions(req)