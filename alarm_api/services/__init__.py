# services/__init__.py — Service dependency factories.

from typing import Annotated

from fastapi import Depends

from alarm_api.repositories.alarm_repository import (
    AlarmRepository,
    alarm_repository,
    get_alarm_repository,
)
from alarm_api.repositories.asset_repository import (
    AssetRepository,
    asset_repository,
    get_asset_repository,
)
from alarm_api.repositories.calculation_repository import (
    CalculationRepository,
    calculation_repository,
    get_calculation_repository,
)
from alarm_api.repositories.kpi_repository import KpiRepository, get_kpi_repository
from alarm_api.services.alarm_service import AlarmService, get_alarm_service
from alarm_api.services.asset_service import AssetService, get_asset_service
from alarm_api.services.calculation_service import CalculationService
from alarm_api.services.recommendation_service import RecommendationService


def get_recommendation_service(
    alarm_repo: Annotated[AlarmRepository, Depends(get_alarm_repository)],
    asset_repo: Annotated[AssetRepository, Depends(get_asset_repository)],
) -> RecommendationService:
    """FastAPI dependency that wires the recommendation service with both repositories."""
    return RecommendationService(alarm_repo=alarm_repo, asset_repo=asset_repo)


def get_calculation_service(
    calc_repo: Annotated[CalculationRepository, Depends(get_calculation_repository)],
    alarm_service: Annotated[AlarmService, Depends(get_alarm_service)],
) -> CalculationService:
    """FastAPI dependency that wires the calculation service with its repo + AlarmService."""
    return CalculationService(calc_repo=calc_repo, alarm_service=alarm_service)


__all__ = [
    # singletons
    "asset_repository",
    "alarm_repository",
    "calculation_repository",
    # dependency callables
    "get_asset_repository",
    "get_alarm_repository",
    "get_calculation_repository",
    "get_asset_service",
    "get_alarm_service",
    "get_recommendation_service",
    "get_calculation_service",
    # classes
    "AssetRepository",
    "AlarmRepository",
    "CalculationRepository",
    "KpiRepository",
    "AssetService",
    "AlarmService",
    "RecommendationService",
    "CalculationService",
]