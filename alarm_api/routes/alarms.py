# routes/alarms.py — Alarm listing, retrieval, and analytics endpoints.

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from alarm_api.models import (
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
from alarm_api.services import AlarmService, get_alarm_service


router = APIRouter(prefix="/alarms", tags=["alarms"])


@router.get("", response_model=AlarmListResponse)
def list_alarms(
    service: Annotated[AlarmService, Depends(get_alarm_service)],
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
    items, total = service.paginated_list(
        asset_id=asset_id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return AlarmListResponse(data=items, page=page, page_size=page_size, total=total)


@router.get("/{alarm_id}", response_model=Alarm)
def get_alarm(
    alarm_id: Annotated[
        str,
        Path(min_length=1, description="Alarm identifier (e.g. 'ALM-0001'). Case-sensitive."),
    ],
    service: Annotated[AlarmService, Depends(get_alarm_service)],
) -> Alarm:
    """Return a single alarm by ID, or 404 if unknown."""
    alarm = service.get_by_id(alarm_id)
    if alarm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"alarm {alarm_id!r} not found",
        )
    return alarm


@router.post("/summary", response_model=AlarmSummaryResponse)
def alarm_summary(
    req: AlarmSummaryRequest,
    service: Annotated[AlarmService, Depends(get_alarm_service)],
) -> AlarmSummaryResponse:
    """Group filtered alarms and compute the requested KPIs."""
    raw_groups, total = service.summarize(
        asset_ids=req.asset_ids,
        time_range=req.time_range,
        severity=req.severity,
        group_by=req.group_by,
        kpis=req.kpis,
    )
    groups = [AlarmSummaryGroup(**g) for g in raw_groups]
    return AlarmSummaryResponse(groups=groups, total_alarms=total)


@router.post("/trends", response_model=AlarmTrendsResponse)
def alarm_trends(
    req: AlarmTrendsRequest,
    service: Annotated[AlarmService, Depends(get_alarm_service)],
) -> AlarmTrendsResponse:
    """Bucket filtered alarms and compute per-bucket metrics."""
    raw_buckets = service.trends(
        asset_ids=req.asset_ids,
        time_range=req.time_range,
        bucket=req.bucket,
        metrics=req.metrics,
    )
    buckets = [AlarmTrendBucket(**b) for b in raw_buckets]
    return AlarmTrendsResponse(buckets=buckets)


@router.post("/correlation", response_model=AlarmCorrelationResponse)
def alarm_correlation(
    req: AlarmCorrelationRequest,
    service: Annotated[AlarmService, Depends(get_alarm_service)],
) -> AlarmCorrelationResponse:
    """Find pairs of distinct alarm_names that co-occur within the lag window."""
    raw_pairs, total = service.correlations(
        asset_ids=req.asset_ids,
        time_range=req.time_range,
        lag_window_minutes=req.lag_window_minutes,
        severity_threshold=req.severity_threshold,
        min_support=req.min_support,
    )
    pairs = [AlarmCorrelationPair(**p) for p in raw_pairs]
    return AlarmCorrelationResponse(pairs=pairs, total_alarms=total)


@router.post("/flood-analysis", response_model=FloodAnalysisResponse)
def flood_analysis(
    req: FloodAnalysisRequest,
    service: Annotated[AlarmService, Depends(get_alarm_service)],
) -> FloodAnalysisResponse:
    """Bin alarms for `unit` and flag windows whose count meets the threshold."""
    raw_windows, flood_count = service.detect_floods(
        unit=req.unit,
        time_range=req.time_range,
        threshold_count=req.threshold_count,
        rolling_window_minutes=req.rolling_window_minutes,
    )
    windows = [FloodWindow(**w) for w in raw_windows]
    return FloodAnalysisResponse(windows=windows, flood_windows_detected=flood_count)


@router.post(
    "/rationalization-candidates", response_model=RationalizationCandidatesResponse
)
def rationalization_candidates(
    req: RationalizationRequest,
    service: Annotated[AlarmService, Depends(get_alarm_service)],
) -> RationalizationCandidatesResponse:
    """Surface chattering or stale alarms as rationalization candidates."""
    raw = service.rationalization_candidates(
        asset_ids=req.asset_ids,
        time_range=req.time_range,
        recurrence_threshold=req.recurrence_threshold,
        stale_minutes_threshold=req.stale_minutes_threshold,
    )
    candidates = [RationalizationCandidate(**c) for c in raw]
    return RationalizationCandidatesResponse(candidates=candidates)


@router.post("/priority-score", response_model=PriorityScoreResponse)
def priority_score(
    req: PriorityScoreRequest,
    service: Annotated[AlarmService, Depends(get_alarm_service)],
) -> PriorityScoreResponse:
    """Compute a simple priority score for a single alarm."""
    alarm = service.get_by_id(req.alarm_id)
    if alarm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"alarm {req.alarm_id!r} not found",
        )
    score, band, factors = service.priority_score(alarm)
    return PriorityScoreResponse(
        alarm_id=alarm.alarm_id,
        score=score,
        band=band,
        factors=factors,
    )