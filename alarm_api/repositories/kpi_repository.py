# repositories/kpi_repository.py — Read-only access to the static KPI catalog.

from alarm_api.data import KPI_DEFINITIONS
from alarm_api.models import KpiDefinition


class KpiRepository:
    """Read-only lookup for the static KPI catalog."""

    def __init__(self, kpis: list[KpiDefinition]) -> None:
        self._kpis = list(kpis)

    def list_all(self) -> list[KpiDefinition]:
        """Return every KPI definition in catalog order."""
        return list(self._kpis)


# Module-level singleton wired to the static catalog.
kpi_repository = KpiRepository(KPI_DEFINITIONS)


def get_kpi_repository() -> KpiRepository:
    """FastAPI dependency that yields the singleton KPI repository."""
    return kpi_repository