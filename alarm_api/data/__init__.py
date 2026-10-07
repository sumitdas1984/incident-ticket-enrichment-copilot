# data/__init__.py — Re-exports for backward-compatible `from alarm_api.data import X` imports.

from alarm_api.data.alarms import ALARMS
from alarm_api.data.assets import ASSETS
from alarm_api.data.kpis import KPI_DEFINITIONS

__all__ = ["ASSETS", "ALARMS", "KPI_DEFINITIONS"]