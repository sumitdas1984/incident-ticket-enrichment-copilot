# models/asset.py — Asset-related Pydantic models

from pydantic import BaseModel, Field


class Asset(BaseModel):
    """An industrial asset registered in the alarm management system."""

    asset_id: str = Field(..., description="Stable, plant-wide unique identifier for the asset.")
    name: str = Field(
        ...,
        description="Human-readable asset name. Searched as a case-insensitive substring.",
    )
    unit: str | None = Field(
        default=None,
        description="Process unit the asset belongs to (e.g. 'Unit 5').",
    )
    site: str | None = Field(
        default=None,
        description="Plant or site the asset belongs to (e.g. 'SouthPlant').",
    )
    asset_type: str | None = Field(
        default=None,
        description="Equipment class (e.g. 'pump', 'compressor', 'motor', 'heat_exchanger', 'cooling_tower').",
    )


class AssetSearchResponse(BaseModel):
    """Response envelope for GET /assets/search. The contract is {results: [Asset, ...]}."""

    results: list[Asset] = Field(
        ...,
        description="Matching assets in deterministic seed order, capped by `limit`.",
    )