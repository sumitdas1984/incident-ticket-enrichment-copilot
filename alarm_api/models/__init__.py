# models/__init__.py — Re-exports for backward-compatible `from alarm_api.models import X` imports.

from alarm_api.models.alarm import (
    Alarm,
    AlarmCorrelationPair,
    AlarmCorrelationRequest,
    AlarmCorrelationResponse,
    AlarmListResponse,
    AlarmSummaryGroup,
    AlarmSummaryRequest,
    AlarmSummaryResponse,
    AlarmTrendBucket,
    AlarmTrendsRequest,
    AlarmTrendsResponse,
    FloodAnalysisRequest,
    FloodAnalysisResponse,
    FloodWindow,
    PriorityScoreRequest,
    PriorityScoreResponse,
    RationalizationCandidatesResponse,
    RationalizationCandidate,
    RationalizationRequest,
)
from alarm_api.models.asset import Asset, AssetSearchResponse
from alarm_api.models.calculation import (
    ExecuteCalculationRequest,
    ExecuteCalculationResponse,
    GenerateCalculationRequest,
    GenerateCalculationResponse,
)
from alarm_api.models.common import TimeRange
from alarm_api.models.kpi import KpiDefinition, KpiDefinitionsResponse
from alarm_api.models.recommendation import (
    HistoricalPattern,
    OperatorAction,
    OperatorActionsRequest,
    OperatorActionsResponse,
    RecommendationAssetContext,
    RelatedAlarm,
)

__all__ = [
    # asset
    "Asset",
    "AssetSearchResponse",
    # alarm
    "Alarm",
    "AlarmListResponse",
    "AlarmCorrelationPair",
    "AlarmCorrelationRequest",
    "AlarmCorrelationResponse",
    "AlarmSummaryGroup",
    "AlarmSummaryRequest",
    "AlarmSummaryResponse",
    "AlarmTrendBucket",
    "AlarmTrendsRequest",
    "AlarmTrendsResponse",
    "FloodAnalysisRequest",
    "FloodAnalysisResponse",
    "FloodWindow",
    "PriorityScoreRequest",
    "PriorityScoreResponse",
    "RationalizationCandidate",
    "RationalizationCandidatesResponse",
    "RationalizationRequest",
    # common
    "TimeRange",
    # recommendation
    "HistoricalPattern",
    "OperatorAction",
    "OperatorActionsRequest",
    "OperatorActionsResponse",
    "RecommendationAssetContext",
    "RelatedAlarm",
    # calculation
    "ExecuteCalculationRequest",
    "ExecuteCalculationResponse",
    "GenerateCalculationRequest",
    "GenerateCalculationResponse",
    # kpi
    "KpiDefinition",
    "KpiDefinitionsResponse",
]