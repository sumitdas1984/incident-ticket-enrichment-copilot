# models/recommendation.py — Operator-action recommendation models

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


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