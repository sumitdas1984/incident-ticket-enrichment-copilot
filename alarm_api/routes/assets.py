# routes/assets.py — Asset endpoints.

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from alarm_api.models import Asset, AssetSearchResponse
from alarm_api.services import AssetService, get_asset_service


router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/search", response_model=AssetSearchResponse)
def search_asset(
    service: Annotated[AssetService, Depends(get_asset_service)],
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
        results=service.search(
            query=normalised_query,
            limit=limit,
            unit=normalised_unit,
        )
    )


@router.get("/{asset_id}/metadata", response_model=Asset)
def get_asset_metadata(
    asset_id: Annotated[
        str,
        Path(
            min_length=1,
            description="Asset identifier (e.g. 'P-101'). Case-sensitive.",
        ),
    ],
    service: Annotated[AssetService, Depends(get_asset_service)],
) -> Asset:
    """Return the full asset record for the given asset_id, or 404 if unknown."""
    asset = service.get_by_id(asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"asset {asset_id!r} not found",
        )
    return asset