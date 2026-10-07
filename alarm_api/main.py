# main.py — FastAPI application
# This is the entry point.

from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Path, Query, status

from alarm_api.data import (
    get_alarm_by_id,
    get_asset_by_id,
    query_alarms,
    search_assets,
)
from alarm_api.models import Alarm, AlarmListResponse, Asset, AssetSearchResponse

app = FastAPI(title="Alarm Management API Simulator")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/assets/{asset_id}/metadata", response_model=Asset)
def get_asset_metadata(
    asset_id: Annotated[
        str,
        Path(
            min_length=1,
            description="Asset identifier (e.g. 'P-101'). Case-sensitive.",
        ),
    ],
) -> Asset:
    """Return the full asset record for the given asset_id, or 404 if unknown."""
    asset = get_asset_by_id(asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"asset {asset_id!r} not found",
        )
    return asset


@app.get("/assets/search", response_model=AssetSearchResponse)
def search_asset(
    query: Annotated[
        str,
        Query(
            min_length=1,
            description="Case-insensitive substring matched against asset `name`.",
        ),
    ],
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Maximum number of results to return (1-100, default 10).",
        ),
    ] = 10,
    unit: Annotated[
        str | None,
        Query(
            description="Optional exact unit filter (e.g. 'Unit 5'). Case-insensitive.",
        ),
    ] = None,
) -> AssetSearchResponse:
    """Search the deterministic asset seed by name substring."""
    normalised_query = query.strip()
    if not normalised_query:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="query must be a non-empty, non-whitespace string",
        )
    normalised_unit = unit.strip() if unit is not None else None
    if normalised_unit == "":
        normalised_unit = None

    return AssetSearchResponse(
        results=search_assets(
            query=normalised_query,
            limit=limit,
            unit=normalised_unit,
        )
    )


@app.get("/alarms", response_model=AlarmListResponse)
def list_alarms(
    asset_id: Annotated[
        str | None,
        Query(description="Filter to alarms for this asset_id only."),
    ] = None,
    page: Annotated[int, Query(ge=1, description="1-indexed page number.")] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100, description="Number of items per page (1-100, default 50)."),
    ] = 50,
    sort_by: Annotated[
        Literal["start_time", "priority", "alarm_id"],
        Query(description="Field to sort by. Severity is intentionally not sortable alphabetically."),
    ] = "start_time",
    sort_order: Annotated[
        Literal["asc", "desc"],
        Query(description="Sort direction."),
    ] = "desc",
) -> AlarmListResponse:
    """List alarms from the deterministic seed with basic filtering, sorting, and pagination."""
    items, total = query_alarms(
        asset_id=asset_id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return AlarmListResponse(data=items, page=page, page_size=page_size, total=total)


@app.get("/alarms/{alarm_id}", response_model=Alarm)
def get_alarm(
    alarm_id: Annotated[
        str,
        Path(min_length=1, description="Alarm identifier (e.g. 'ALM-0001'). Case-sensitive."),
    ],
) -> Alarm:
    """Return a single alarm by ID, or 404 if unknown."""
    alarm = get_alarm_by_id(alarm_id)
    if alarm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"alarm {alarm_id!r} not found",
        )
    return alarm


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)