# data/kpis.py — Static catalog of supported KPIs returned by /analytics/kpi-definitions.

from alarm_api.models import KpiDefinition


KPI_DEFINITIONS: list[KpiDefinition] = [
    KpiDefinition(
        kpi_id="alarm_count",
        name="Alarm count",
        description="Total number of alarms in the selected window.",
        unit="alarms",
        category="volume",
    ),
    KpiDefinition(
        kpi_id="recurring_rate",
        name="Recurring alarm rate",
        description="Fraction of alarms whose tag has fired more than once in the window.",
        unit="ratio",
        category="quality",
    ),
    KpiDefinition(
        kpi_id="avg_ack_delay_seconds",
        name="Average acknowledgement delay",
        description="Mean (acknowledged_at - start_time) over acknowledged alarms.",
        unit="seconds",
        category="responsiveness",
    ),
    KpiDefinition(
        kpi_id="flood_index",
        name="Flood index",
        description="Fraction of minute-bins whose alarm count meets the flood threshold.",
        unit="ratio",
        category="quality",
    ),
    KpiDefinition(
        kpi_id="avg_priority",
        name="Average priority",
        description="Mean configured priority across alarms.",
        unit="score",
        category="priority",
    ),
    KpiDefinition(
        kpi_id="active_alarm_count",
        name="Active alarm count",
        description="Number of alarms currently in the 'active' state.",
        unit="alarms",
        category="state",
    ),
]