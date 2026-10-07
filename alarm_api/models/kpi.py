# models/kpi.py — KPI catalog models

from pydantic import BaseModel


class KpiDefinition(BaseModel):
    kpi_id: str
    name: str
    description: str
    unit: str | None = None
    category: str


class KpiDefinitionsResponse(BaseModel):
    kpis: list[KpiDefinition]