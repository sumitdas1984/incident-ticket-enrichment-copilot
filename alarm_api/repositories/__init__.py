# repositories/__init__.py — Re-exports for repository singletons and dependency callables.

from alarm_api.repositories.alarm_repository import (
    alarm_repository,
    get_alarm_repository,
)
from alarm_api.repositories.asset_repository import (
    asset_repository,
    get_asset_repository,
)
from alarm_api.repositories.calculation_repository import (
    calculation_repository,
    get_calculation_repository,
)
from alarm_api.repositories.kpi_repository import get_kpi_repository, kpi_repository

__all__ = [
    "alarm_repository",
    "asset_repository",
    "calculation_repository",
    "kpi_repository",
    "get_alarm_repository",
    "get_asset_repository",
    "get_calculation_repository",
    "get_kpi_repository",
]