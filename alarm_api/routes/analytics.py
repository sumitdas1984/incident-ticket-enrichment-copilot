# routes/analytics.py — Static KPI catalog endpoint.

from typing import Annotated

from fastapi import APIRouter, Depends

from alarm_api.models import KpiDefinitionsResponse
from alarm_api.repositories.kpi_repository import KpiRepository, get_kpi_repository


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/kpi-definitions", response_model=KpiDefinitionsResponse)
def kpi_definitions(
    repo: Annotated[KpiRepository, Depends(get_kpi_repository)],
) -> KpiDefinitionsResponse:
    """Return the static catalog of supported KPIs."""
    return KpiDefinitionsResponse(kpis=repo.list_all())