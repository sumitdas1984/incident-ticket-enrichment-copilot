# routes/recommendations.py — Operator-action recommendation endpoint.

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from alarm_api.models import (
    HistoricalPattern,
    OperatorAction,
    OperatorActionsRequest,
    OperatorActionsResponse,
    RecommendationAssetContext,
    RelatedAlarm,
)
from alarm_api.services import (
    AssetService,
    RecommendationService,
    get_asset_service,
    get_recommendation_service,
)


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/operator-actions", response_model=OperatorActionsResponse)
def operator_actions(
    req: OperatorActionsRequest,
    rec_service: Annotated[RecommendationService, Depends(get_recommendation_service)],
    asset_service: Annotated[AssetService, Depends(get_asset_service)],
) -> OperatorActionsResponse:
    """Return a deterministic set of operator-action recommendations for the given alarm."""
    alarm = rec_service.get_alarm_by_id(req.alarm_id)
    if alarm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"alarm {req.alarm_id!r} not found",
        )

    related = rec_service.related_alarms(alarm) if req.include_related else []
    historical = rec_service.historical_alarms(alarm) if req.include_historical_pattern else []
    historical_summary = (
        rec_service.historical_pattern(alarm) if req.include_historical_pattern else None
    )

    asset_ctx: RecommendationAssetContext | None = None
    if req.include_asset_context:
        asset = asset_service.get_by_id(alarm.asset_id)
        if asset is not None:
            asset_ctx = RecommendationAssetContext(**rec_service.asset_context(asset))  # type: ignore[arg-type]

    raw_actions = rec_service.build_operator_actions(
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