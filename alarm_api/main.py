# main.py — FastAPI application
# This is the entry point.

from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Path, Query, status

from alarm_api.data import (
    KPI_DEFINITIONS,
    asset_context_for,
    build_operator_actions,
    compute_alarm_trends,
    compute_correlations,
    compute_priority_score,
    detect_floods,
    execute_calculation,
    find_rationalization_candidates,
    generate_calculation,
    get_alarm_by_id,
    get_asset_by_id,
    historical_alarms_for,
    historical_pattern_for,
    query_alarms,
    related_alarms_for,
    search_assets,
    summarize_alarms,
)
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
    Asset,
    AssetSearchResponse,
    ExecuteCalculationRequest,
    ExecuteCalculationResponse,
    FloodAnalysisRequest,
    FloodAnalysisResponse,
    FloodWindow,
    GenerateCalculationRequest,
    GenerateCalculationResponse,
    HistoricalPattern,
    KpiDefinitionsResponse,
    OperatorAction,
    OperatorActionsRequest,
    OperatorActionsResponse,
    PriorityScoreRequest,
    PriorityScoreResponse,
    RationalizationCandidatesResponse,
    RationalizationCandidate,
    RationalizationRequest,
    RecommendationAssetContext,
    RelatedAlarm,
)

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


# ----- Phase 4: alarm analytics -----


@app.post("/alarms/summary", response_model=AlarmSummaryResponse)
def alarm_summary(req: AlarmSummaryRequest) -> AlarmSummaryResponse:
    """Group filtered alarms and compute the requested KPIs."""
    raw_groups, total = summarize_alarms(
        asset_ids=req.asset_ids,
        time_range=req.time_range,
        severity=req.severity,
        group_by=req.group_by,
        kpis=req.kpis,
    )
    groups = [AlarmSummaryGroup(**g) for g in raw_groups]
    return AlarmSummaryResponse(groups=groups, total_alarms=total)


@app.post("/alarms/trends", response_model=AlarmTrendsResponse)
def alarm_trends(req: AlarmTrendsRequest) -> AlarmTrendsResponse:
    """Bucket filtered alarms and compute per-bucket metrics."""
    raw_buckets = compute_alarm_trends(
        asset_ids=req.asset_ids,
        time_range=req.time_range,
        bucket=req.bucket,
        metrics=req.metrics,
    )
    buckets = [AlarmTrendBucket(**b) for b in raw_buckets]
    return AlarmTrendsResponse(buckets=buckets)


@app.post("/alarms/correlation", response_model=AlarmCorrelationResponse)
def alarm_correlation(req: AlarmCorrelationRequest) -> AlarmCorrelationResponse:
    """Find pairs of distinct alarm_names that co-occur within the lag window."""
    raw_pairs, total = compute_correlations(
        asset_ids=req.asset_ids,
        time_range=req.time_range,
        lag_window_minutes=req.lag_window_minutes,
        severity_threshold=req.severity_threshold,
        min_support=req.min_support,
    )
    pairs = [AlarmCorrelationPair(**p) for p in raw_pairs]
    return AlarmCorrelationResponse(pairs=pairs, total_alarms=total)


@app.post("/alarms/flood-analysis", response_model=FloodAnalysisResponse)
def flood_analysis(req: FloodAnalysisRequest) -> FloodAnalysisResponse:
    """Bin alarms for `unit` and flag windows whose count meets the threshold."""
    raw_windows, flood_count = detect_floods(
        unit=req.unit,
        time_range=req.time_range,
        threshold_count=req.threshold_count,
        rolling_window_minutes=req.rolling_window_minutes,
    )
    windows = [FloodWindow(**w) for w in raw_windows]
    return FloodAnalysisResponse(windows=windows, flood_windows_detected=flood_count)


@app.post(
    "/alarms/rationalization-candidates", response_model=RationalizationCandidatesResponse
)
def rationalization_candidates(
    req: RationalizationRequest,
) -> RationalizationCandidatesResponse:
    """Surface chattering or stale alarms as rationalization candidates."""
    raw = find_rationalization_candidates(
        asset_ids=req.asset_ids,
        time_range=req.time_range,
        recurrence_threshold=req.recurrence_threshold,
        stale_minutes_threshold=req.stale_minutes_threshold,
    )
    candidates = [RationalizationCandidate(**c) for c in raw]
    return RationalizationCandidatesResponse(candidates=candidates)


@app.post("/alarms/priority-score", response_model=PriorityScoreResponse)
def priority_score(req: PriorityScoreRequest) -> PriorityScoreResponse:
    """Compute a simple priority score for a single alarm."""
    alarm = get_alarm_by_id(req.alarm_id)
    if alarm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"alarm {req.alarm_id!r} not found",
        )
    score, band, factors = compute_priority_score(alarm)
    return PriorityScoreResponse(
        alarm_id=alarm.alarm_id,
        score=score,
        band=band,
        factors=factors,
    )


# ----- Phase 5: operator-action recommendations -----


@app.post("/recommendations/operator-actions", response_model=OperatorActionsResponse)
def operator_actions(req: OperatorActionsRequest) -> OperatorActionsResponse:
    """Return a deterministic set of operator-action recommendations for the given alarm."""
    alarm = get_alarm_by_id(req.alarm_id)
    if alarm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"alarm {req.alarm_id!r} not found",
        )

    related = related_alarms_for(alarm) if req.include_related else []
    historical = historical_alarms_for(alarm) if req.include_historical_pattern else []
    historical_summary = (
        historical_pattern_for(alarm) if req.include_historical_pattern else None
    )

    asset_ctx: RecommendationAssetContext | None = None
    if req.include_asset_context:
        asset = get_asset_by_id(alarm.asset_id)
        if asset is not None:
            asset_ctx = RecommendationAssetContext(**asset_context_for(asset))  # type: ignore[arg-type]

    raw_actions = build_operator_actions(
        alarm,
        related_count=len(related),
        historical_count=len(historical) + 1,  # +1 for the current alarm
    )
    actions = [OperatorAction(**a) for a in raw_actions]  # type: ignore[arg-type]

    return OperatorActionsResponse(
        alarm_id=alarm.alarm_id,
        actions=actions,
        related_alarms=[
            RelatedAlarm(
                alarm_id=a.alarm_id,
                alarm_name=a.alarm_name,
                relationship="same_asset_within_60min",
                start_time=a.start_time,
            )
            for a in related
        ],
        asset_context=asset_ctx,
        historical_pattern=HistoricalPattern(**historical_summary) if historical_summary else None,  # type: ignore[arg-type]
    )


# ----- Phase 6: calculation code & KPI definitions -----


@app.post("/calculation-code/generate", response_model=GenerateCalculationResponse)
def calc_generate(req: GenerateCalculationRequest) -> GenerateCalculationResponse:
    """Create a new calculation record and return its ID + persisted config."""
    record = generate_calculation(req.calculation_type, req.filters)
    return GenerateCalculationResponse(**record)  # type: ignore[arg-type]


@app.post("/calculation-code/execute", response_model=ExecuteCalculationResponse)
def calc_execute(req: ExecuteCalculationRequest) -> ExecuteCalculationResponse:
    """Run a previously generated calculation."""
    record = execute_calculation(req.calculation_id, req.filters)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"calculation {req.calculation_id!r} not found",
        )
    return ExecuteCalculationResponse(
        calculation_id=str(record["calculation_id"]),
        calculation_type=str(record["calculation_type"]),
        result=record["result"],  # type: ignore[arg-type]
    )


@app.get("/analytics/kpi-definitions", response_model=KpiDefinitionsResponse)
def kpi_definitions() -> KpiDefinitionsResponse:
    """Return the static catalog of supported KPIs."""
    return KpiDefinitionsResponse(kpis=KPI_DEFINITIONS)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)