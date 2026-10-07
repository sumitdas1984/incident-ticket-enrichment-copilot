# models.py — API data structures
# This defines what our API data looks like using Pydantic.

from datetime import datetime

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


class Alarm(BaseModel):
    """An alarm event recorded against an asset."""

    alarm_id: str = Field(..., description="Unique alarm identifier (e.g. 'ALM-0001').")
    asset_id: str = Field(..., description="ID of the asset this alarm belongs to.")
    alarm_name: str = Field(
        ...,
        description="Short alarm tag (e.g. 'P-101/HI_DISCHARGE_PRESSURE').",
    )
    severity: str = Field(
        ...,
        description="Severity bucket: low | medium | high | critical.",
    )
    state: str = Field(
        ...,
        description="Alarm state: active | acknowledged | cleared | resolved.",
    )
    start_time: datetime = Field(..., description="When the alarm first activated.")
    end_time: datetime | None = Field(
        default=None,
        description="When the alarm cleared or resolved, if applicable.",
    )
    asset_name: str | None = Field(
        default=None,
        description="Denormalised asset name, returned for convenience.",
    )
    unit: str | None = Field(
        default=None,
        description="Denormalised process unit, returned for convenience.",
    )
    site: str | None = Field(
        default=None,
        description="Denormalised site, returned for convenience.",
    )
    priority: int | None = Field(
        default=None,
        description="Computed priority (lower value = more urgent).",
    )
    acknowledged_at: datetime | None = Field(
        default=None,
        description="When the operator acknowledged the alarm.",
    )
    acknowledged_by: str | None = Field(
        default=None,
        description="Operator who acknowledged the alarm.",
    )
    description: str | None = Field(
        default=None,
        description="Free-text description or operator-facing message.",
    )


class AlarmListResponse(BaseModel):
    """Paginated response envelope for GET /alarms. Mirrors the Postman contract (`data`, not `items`)."""

    data: list[Alarm] = Field(..., description="Alarms on the current page.")
    page: int = Field(..., description="1-indexed page number.")
    page_size: int = Field(..., description="Number of items per page.")
    total: int = Field(..., description="Total number of alarms matching the filter.")