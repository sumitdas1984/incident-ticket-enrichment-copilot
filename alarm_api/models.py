# models.py — API data structures
# This defines what our API data looks like using Pydantic.

from datetime import datetime
from typing import Literal

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


# ----- Phase 4: analytics request/response models -----


class TimeRange(BaseModel):
    """Inclusive time window used by analytics endpoints."""

    start_time: datetime = Field(..., description="Window start (inclusive).")
    end_time: datetime = Field(..., description="Window end (inclusive).")


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


# ----- Phase 5: operator-action recommendations -----


class OperatorActionsRequest(BaseModel):
    alarm_id: str = Field(..., min_length=1)
    include_related: bool = Field(default=True, description="Include related alarms in the response.")
    include_asset_context: bool = Field(default=True, description="Include asset context in the response.")
    include_historical_pattern: bool = Field(
        default=True,
        description="Include historical pattern summary in the response.",
    )


class OperatorAction(BaseModel):
    action_id: str = Field(..., description="Stable ID within this response (e.g. 'ACT-001').")
    title: str
    description: str
    priority: Literal["low", "medium", "high", "critical"]
    rationale: str
    category: Literal["immediate_response", "investigation", "mitigation", "documentation"]


class RelatedAlarm(BaseModel):
    alarm_id: str
    alarm_name: str
    relationship: str = Field(..., description="Why this alarm is related (e.g. 'same_asset_within_60min').")
    start_time: datetime


class RecommendationAssetContext(BaseModel):
    asset_id: str
    name: str
    unit: str | None
    site: str | None
    asset_type: str | None
    active_alarm_count: int = Field(..., description="Count of `active` alarms currently on this asset.")


class HistoricalPattern(BaseModel):
    alarm_name: str
    occurrence_count: int
    last_occurrence: datetime | None
    common_actions: list[str]


class OperatorActionsResponse(BaseModel):
    alarm_id: str
    actions: list[OperatorAction]
    related_alarms: list[RelatedAlarm] = Field(default_factory=list)
    asset_context: RecommendationAssetContext | None = None
    historical_pattern: HistoricalPattern | None = None


# ----- Phase 6: calculation code & KPI definitions -----


class GenerateCalculationRequest(BaseModel):
    calculation_type: str = Field(
        ...,
        min_length=1,
        description="Type of calculation to generate (e.g. 'alarm_flood_index', 'alarm_count').",
    )
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Filters persisted with the calculation and applied at execute time. "
            "Recognised keys: unit, asset_ids (comma-separated), start_time, end_time."
        ),
    )


class GenerateCalculationResponse(BaseModel):
    calculation_id: str = Field(..., description="Unique ID used by /calculation-code/execute.")
    calculation_type: str
    filters: dict[str, str]
    code: str = Field(..., description="Human-readable description of what the calculation does.")


class ExecuteCalculationRequest(BaseModel):
    calculation_id: str = Field(..., min_length=1)
    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Optional override filters merged on top of the stored filters.",
    )


class ExecuteCalculationResponse(BaseModel):
    calculation_id: str
    calculation_type: str
    result: dict[str, float | int | str] = Field(
        ...,
        description="Computed metrics. Shape depends on the calculation_type.",
    )


class KpiDefinition(BaseModel):
    kpi_id: str
    name: str
    description: str
    unit: str | None = None
    category: str


class KpiDefinitionsResponse(BaseModel):
    kpis: list[KpiDefinition]