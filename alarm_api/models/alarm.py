# models/alarm.py — Alarm models, list responses, and analytics request/response models

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from alarm_api.models.common import TimeRange


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


# ----- Phase 4: analytics request/response models -----


class AlarmSummaryRequest(BaseModel):
    asset_ids: list[str] | None = Field(
        default=None,
        description="Filter to these asset_ids. None means all assets.",
    )
    time_range: TimeRange | None = Field(
        default=None,
        description="Filter to alarms starting in this window. None means all time.",
    )
    severity: list[str] | None = Field(
        default=None,
        description="Filter to alarms of these severities. None means all severities.",
    )
    group_by: list[str] = Field(
        default_factory=lambda: ["alarm_name"],
        description="Alarm fields to group by (e.g. ['alarm_name'], ['asset_id']).",
    )
    kpis: list[str] = Field(
        default_factory=lambda: ["alarm_count"],
        description=(
            "KPIs to compute per group. Supported: alarm_count, recurring_rate, "
            "avg_ack_delay_seconds."
        ),
    )


class AlarmSummaryGroup(BaseModel):
    key: dict[str, str] = Field(..., description="Group key as {field_name: field_value} pairs.")
    metrics: dict[str, float | int] = Field(..., description="Computed KPIs for this group.")


class AlarmSummaryResponse(BaseModel):
    groups: list[AlarmSummaryGroup] = Field(..., description="One entry per distinct group key.")
    total_alarms: int = Field(..., description="Total alarms matching the filters, before grouping.")


class AlarmTrendsRequest(BaseModel):
    asset_ids: list[str] | None = None
    time_range: TimeRange | None = None
    bucket: Literal["hourly", "daily", "weekly"] = "daily"
    metrics: list[Literal["alarm_count", "avg_ack_delay_seconds"]] = Field(
        default_factory=lambda: ["alarm_count"],
    )


class AlarmTrendBucket(BaseModel):
    bucket_start: datetime = Field(..., description="Start of the time bucket.")
    metrics: dict[str, float | int] = Field(..., description="Computed metrics for this bucket.")


class AlarmTrendsResponse(BaseModel):
    buckets: list[AlarmTrendBucket] = Field(..., description="Time-ordered buckets.")


class AlarmCorrelationRequest(BaseModel):
    asset_ids: list[str] | None = None
    time_range: TimeRange | None = None
    correlation_method: Literal["cooccurrence"] = "cooccurrence"
    lag_window_minutes: int = Field(default=15, ge=0)
    severity_threshold: Literal["low", "medium", "high", "critical"] = "medium"
    min_support: int = Field(default=1, ge=1)


class AlarmCorrelationPair(BaseModel):
    alarm_name_a: str
    alarm_name_b: str
    cooccurrence_count: int
    support: float = Field(..., description="cooccurrence_count / total_alarms in the filtered set.")


class AlarmCorrelationResponse(BaseModel):
    pairs: list[AlarmCorrelationPair]
    total_alarms: int


class FloodAnalysisRequest(BaseModel):
    unit: str = Field(..., min_length=1)
    time_range: TimeRange | None = None
    threshold_count: int = Field(default=10, ge=1)
    rolling_window_minutes: int = Field(default=10, ge=1)


class FloodWindow(BaseModel):
    window_start: datetime
    alarm_count: int
    is_flood: bool


class FloodAnalysisResponse(BaseModel):
    windows: list[FloodWindow]
    flood_windows_detected: int


class RationalizationRequest(BaseModel):
    asset_ids: list[str] | None = None
    time_range: TimeRange | None = None
    recurrence_threshold: int = Field(default=5, ge=2)
    stale_minutes_threshold: int = Field(default=180, ge=1)


class RationalizationCandidate(BaseModel):
    alarm_name: str
    asset_id: str
    occurrence_count: int
    reason: Literal["chattering", "stale"]


class RationalizationCandidatesResponse(BaseModel):
    candidates: list[RationalizationCandidate]


class PriorityScoreRequest(BaseModel):
    alarm_id: str = Field(..., min_length=1)


class PriorityScoreResponse(BaseModel):
    alarm_id: str
    score: float
    band: Literal["low", "medium", "high", "critical"]
    factors: dict[str, float | int | str] = Field(
        ...,
        description="Component contributions that produced the score.",
    )