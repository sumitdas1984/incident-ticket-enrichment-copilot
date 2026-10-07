# data.py — deterministic seed data
# This contains our initial fake industrial data.

from datetime import datetime, timezone

from alarm_api.models import Alarm, Asset


ASSETS: list[Asset] = [
    Asset(
        asset_id="P-101",
        name="Boiler Feed Pump 101",
        unit="Unit 5",
        site="SouthPlant",
        asset_type="pump",
    ),
    Asset(
        asset_id="P-102",
        name="Boiler Feed Pump 102",
        unit="Unit 5",
        site="SouthPlant",
        asset_type="pump",
    ),
    Asset(
        asset_id="C-201",
        name="Air Compressor 201",
        unit="Unit 5",
        site="SouthPlant",
        asset_type="compressor",
    ),
    Asset(
        asset_id="C-203",
        name="Centrifugal Compressor 203",
        unit="Unit 7",
        site="SouthPlant",
        asset_type="compressor",
    ),
    Asset(
        asset_id="M-4501",
        name="Cooling Tower Fan Motor 4501",
        unit="Unit 5",
        site="SouthPlant",
        asset_type="motor",
    ),
    Asset(
        asset_id="M-4502",
        name="Conveyor Drive Motor 4502",
        unit="Unit 5",
        site="SouthPlant",
        asset_type="motor",
    ),
    Asset(
        asset_id="M-7701",
        name="Reflux Pump Motor 7701",
        unit="Unit 7",
        site="SouthPlant",
        asset_type="motor",
    ),
    Asset(
        asset_id="HX-301",
        name="Feedwater Heat Exchanger 301",
        unit="Unit 5",
        site="SouthPlant",
        asset_type="heat_exchanger",
    ),
    Asset(
        asset_id="HX-702",
        name="Overhead Condenser 702",
        unit="Unit 7",
        site="SouthPlant",
        asset_type="heat_exchanger",
    ),
    Asset(
        asset_id="CT-501",
        name="Cooling Tower 501",
        unit="Unit 5",
        site="SouthPlant",
        asset_type="cooling_tower",
    ),
    Asset(
        asset_id="T-601",
        name="Crude Distillation Tower 601",
        unit="Unit 7",
        site="EastRefinery",
        asset_type="column",
    ),
    Asset(
        asset_id="P-803",
        name="Slurry Recirc Pump 803",
        unit="Unit 7",
        site="EastRefinery",
        asset_type="pump",
    ),
]


def search_assets(query: str, limit: int = 10, unit: str | None = None) -> list[Asset]:
    """Return up to `limit` assets whose `name` contains `query` (case-insensitive substring).

    If `unit` is given, only assets whose `unit` exactly matches (case-insensitive)
    are returned. Insertion order is preserved.
    """
    needle = query.lower().strip()
    unit_filter = unit.lower().strip() if unit is not None else None

    results: list[Asset] = []
    for asset in ASSETS:
        if needle not in asset.name.lower():
            continue
        if unit_filter is not None:
            if asset.unit is None or asset.unit.lower() != unit_filter:
                continue
        results.append(asset)
        if len(results) >= limit:
            break
    return results


_ASSETS_BY_ID: dict[str, Asset] = {asset.asset_id: asset for asset in ASSETS}


def get_asset_by_id(asset_id: str) -> Asset | None:
    """Return the asset with the given `asset_id`, or None if no match.

    Match is case-sensitive — `asset_id` is treated as a stable identifier.
    """
    return _ASSETS_BY_ID.get(asset_id)


ALARMS: list[Alarm] = [
    # P-101 — Boiler Feed Pump 101 (Unit 5)
    Alarm(
        alarm_id="ALM-0001",
        asset_id="P-101",
        asset_name="Boiler Feed Pump 101",
        unit="Unit 5",
        site="SouthPlant",
        alarm_name="P-101/HI_DISCHARGE_PRESSURE",
        severity="high",
        state="active",
        start_time=datetime(2026, 6, 28, 14, 32, 0, tzinfo=timezone.utc),
        priority=2,
        description="Discharge pressure crossed the high-high threshold.",
    ),
    Alarm(
        alarm_id="ALM-0002",
        asset_id="P-101",
        asset_name="Boiler Feed Pump 101",
        unit="Unit 5",
        site="SouthPlant",
        alarm_name="P-101/HI_VIBRATION",
        severity="medium",
        state="acknowledged",
        start_time=datetime(2026, 6, 25, 9, 14, 0, tzinfo=timezone.utc),
        acknowledged_at=datetime(2026, 6, 25, 9, 22, 0, tzinfo=timezone.utc),
        acknowledged_by="op.smith",
        priority=3,
        description="Vibration trending upward over the last 24 hours.",
    ),
    Alarm(
        alarm_id="ALM-0003",
        asset_id="P-101",
        asset_name="Boiler Feed Pump 101",
        unit="Unit 5",
        site="SouthPlant",
        alarm_name="P-101/LO_FLOW",
        severity="critical",
        state="resolved",
        start_time=datetime(2026, 6, 18, 3, 5, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 6, 18, 5, 12, 0, tzinfo=timezone.utc),
        priority=1,
        acknowledged_at=datetime(2026, 6, 18, 3, 8, 0, tzinfo=timezone.utc),
        acknowledged_by="op.jones",
        description="Brief flow loss; pump restarted after cooldown.",
    ),
    # P-102 — Boiler Feed Pump 102 (Unit 5)
    Alarm(
        alarm_id="ALM-0004",
        asset_id="P-102",
        asset_name="Boiler Feed Pump 102",
        unit="Unit 5",
        site="SouthPlant",
        alarm_name="P-102/HI_MOTOR_TEMP",
        severity="low",
        state="cleared",
        start_time=datetime(2026, 5, 30, 11, 0, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 5, 30, 13, 45, 0, tzinfo=timezone.utc),
        priority=4,
        description="Motor winding temperature spike during peak load.",
    ),
    Alarm(
        alarm_id="ALM-0005",
        asset_id="P-102",
        asset_name="Boiler Feed Pump 102",
        unit="Unit 5",
        site="SouthPlant",
        alarm_name="P-102/HI_DISCHARGE_PRESSURE",
        severity="high",
        state="active",
        start_time=datetime(2026, 6, 27, 16, 48, 0, tzinfo=timezone.utc),
        priority=2,
        description="Discharge pressure above alarm setpoint.",
    ),
    # C-201 — Air Compressor 201 (Unit 5)
    Alarm(
        alarm_id="ALM-0006",
        asset_id="C-201",
        asset_name="Air Compressor 201",
        unit="Unit 5",
        site="SouthPlant",
        alarm_name="C-201/HI_OUTLET_TEMP",
        severity="medium",
        state="acknowledged",
        start_time=datetime(2026, 6, 15, 12, 0, 0, tzinfo=timezone.utc),
        acknowledged_at=datetime(2026, 6, 15, 12, 14, 0, tzinfo=timezone.utc),
        acknowledged_by="op.singh",
        priority=3,
        description="Compressor outlet temperature elevated.",
    ),
    Alarm(
        alarm_id="ALM-0007",
        asset_id="C-201",
        asset_name="Air Compressor 201",
        unit="Unit 5",
        site="SouthPlant",
        alarm_name="C-201/HI_VIBRATION",
        severity="high",
        state="active",
        start_time=datetime(2026, 6, 26, 8, 22, 0, tzinfo=timezone.utc),
        priority=2,
        description="Bearing vibration above warning band.",
    ),
    # C-203 — Centrifugal Compressor 203 (Unit 7)
    Alarm(
        alarm_id="ALM-0008",
        asset_id="C-203",
        asset_name="Centrifugal Compressor 203",
        unit="Unit 7",
        site="SouthPlant",
        alarm_name="C-203/SURGE_DETECTED",
        severity="critical",
        state="acknowledged",
        start_time=datetime(2026, 6, 20, 21, 14, 0, tzinfo=timezone.utc),
        acknowledged_at=datetime(2026, 6, 20, 21, 18, 0, tzinfo=timezone.utc),
        acknowledged_by="op.kim",
        priority=1,
        description="Compressor surge detected; anti-surge valve opened.",
    ),
    Alarm(
        alarm_id="ALM-0009",
        asset_id="C-203",
        asset_name="Centrifugal Compressor 203",
        unit="Unit 7",
        site="SouthPlant",
        alarm_name="C-203/HI_DISCHARGE_TEMP",
        severity="medium",
        state="cleared",
        start_time=datetime(2026, 6, 10, 6, 33, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 6, 10, 11, 0, 0, tzinfo=timezone.utc),
        priority=3,
        description="Discharge temperature spike during startup.",
    ),
    # M-4501 — Cooling Tower Fan Motor 4501 (Unit 5)
    Alarm(
        alarm_id="ALM-0010",
        asset_id="M-4501",
        asset_name="Cooling Tower Fan Motor 4501",
        unit="Unit 5",
        site="SouthPlant",
        alarm_name="M-4501/HI_VIBRATION",
        severity="medium",
        state="active",
        start_time=datetime(2026, 6, 29, 3, 45, 0, tzinfo=timezone.utc),
        priority=3,
        description="Fan motor vibration trending above baseline.",
    ),
    # M-4502 — Conveyor Drive Motor 4502 (Unit 5)
    Alarm(
        alarm_id="ALM-0011",
        asset_id="M-4502",
        asset_name="Conveyor Drive Motor 4502",
        unit="Unit 5",
        site="SouthPlant",
        alarm_name="M-4502/OVERCURRENT",
        severity="high",
        state="acknowledged",
        start_time=datetime(2026, 6, 22, 10, 14, 0, tzinfo=timezone.utc),
        acknowledged_at=datetime(2026, 6, 22, 10, 20, 0, tzinfo=timezone.utc),
        acknowledged_by="op.das",
        priority=2,
        description="Drive motor current exceeded rated value.",
    ),
    Alarm(
        alarm_id="ALM-0012",
        asset_id="M-4502",
        asset_name="Conveyor Drive Motor 4502",
        unit="Unit 5",
        site="SouthPlant",
        alarm_name="M-4502/HI_BEARING_TEMP",
        severity="low",
        state="resolved",
        start_time=datetime(2026, 6, 12, 9, 18, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 6, 12, 14, 22, 0, tzinfo=timezone.utc),
        priority=4,
        description="Bearing temperature elevated; lubrication scheduled.",
    ),
    # M-7701 — Reflux Pump Motor 7701 (Unit 7)
    Alarm(
        alarm_id="ALM-0013",
        asset_id="M-7701",
        asset_name="Reflux Pump Motor 7701",
        unit="Unit 7",
        site="SouthPlant",
        alarm_name="M-7701/HI_VIBRATION",
        severity="medium",
        state="acknowledged",
        start_time=datetime(2026, 6, 28, 22, 47, 0, tzinfo=timezone.utc),
        acknowledged_at=datetime(2026, 6, 28, 22, 55, 0, tzinfo=timezone.utc),
        acknowledged_by="op.patel",
        priority=3,
        description="Motor vibration high; awaiting maintenance window.",
    ),
    Alarm(
        alarm_id="ALM-0014",
        asset_id="M-7701",
        asset_name="Reflux Pump Motor 7701",
        unit="Unit 7",
        site="SouthPlant",
        alarm_name="M-7701/OVERCURRENT",
        severity="critical",
        state="active",
        start_time=datetime(2026, 6, 23, 17, 30, 0, tzinfo=timezone.utc),
        priority=1,
        description="Sustained overcurrent on motor; investigate load.",
    ),
    # HX-301 — Feedwater Heat Exchanger 301 (Unit 5)
    Alarm(
        alarm_id="ALM-0015",
        asset_id="HX-301",
        asset_name="Feedwater Heat Exchanger 301",
        unit="Unit 5",
        site="SouthPlant",
        alarm_name="HX-301/HI_OUTLET_TEMP",
        severity="low",
        state="cleared",
        start_time=datetime(2026, 5, 22, 14, 0, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 5, 22, 16, 30, 0, tzinfo=timezone.utc),
        priority=4,
        description="Outlet temperature drifted above band.",
    ),
    # HX-702 — Overhead Condenser 702 (Unit 7)
    Alarm(
        alarm_id="ALM-0016",
        asset_id="HX-702",
        asset_name="Overhead Condenser 702",
        unit="Unit 7",
        site="SouthPlant",
        alarm_name="HX-702/LO_CONDENSATE_FLOW",
        severity="high",
        state="active",
        start_time=datetime(2026, 6, 29, 11, 18, 0, tzinfo=timezone.utc),
        priority=2,
        description="Condensate flow dropped below low-low setpoint.",
    ),
    # CT-501 — Cooling Tower 501 (Unit 5)
    Alarm(
        alarm_id="ALM-0017",
        asset_id="CT-501",
        asset_name="Cooling Tower 501",
        unit="Unit 5",
        site="SouthPlant",
        alarm_name="CT-501/FAN_VFD_FAULT",
        severity="medium",
        state="acknowledged",
        start_time=datetime(2026, 6, 21, 15, 42, 0, tzinfo=timezone.utc),
        acknowledged_at=datetime(2026, 6, 21, 15, 50, 0, tzinfo=timezone.utc),
        acknowledged_by="op.smith",
        priority=3,
        description="VFD reported a fault on fan 1; running on bypass.",
    ),
    # T-601 — Crude Distillation Tower 601 (Unit 7)
    Alarm(
        alarm_id="ALM-0018",
        asset_id="T-601",
        asset_name="Crude Distillation Tower 601",
        unit="Unit 7",
        site="EastRefinery",
        alarm_name="T-601/HI_TOP_TEMP",
        severity="critical",
        state="active",
        start_time=datetime(2026, 6, 29, 9, 30, 0, tzinfo=timezone.utc),
        priority=1,
        description="Tower top temperature above safe operating limit.",
    ),
    # P-803 — Slurry Recirc Pump 803 (Unit 7)
    Alarm(
        alarm_id="ALM-0019",
        asset_id="P-803",
        asset_name="Slurry Recirc Pump 803",
        unit="Unit 7",
        site="EastRefinery",
        alarm_name="P-803/HI_CIRCULATION_PRESSURE",
        severity="high",
        state="active",
        start_time=datetime(2026, 6, 28, 19, 55, 0, tzinfo=timezone.utc),
        priority=2,
        description="Circulation pressure trending high; check for line restriction.",
    ),
    Alarm(
        alarm_id="ALM-0020",
        asset_id="P-803",
        asset_name="Slurry Recirc Pump 803",
        unit="Unit 7",
        site="EastRefinery",
        alarm_name="P-803/SEAL_LEAK",
        severity="medium",
        state="acknowledged",
        start_time=datetime(2026, 6, 24, 13, 20, 0, tzinfo=timezone.utc),
        acknowledged_at=datetime(2026, 6, 24, 13, 28, 0, tzinfo=timezone.utc),
        acknowledged_by="op.das",
        priority=3,
        description="Mechanical seal showing minor leakage.",
    ),
]


_ALARMS_BY_ID: dict[str, Alarm] = {alarm.alarm_id: alarm for alarm in ALARMS}


def get_alarm_by_id(alarm_id: str) -> Alarm | None:
    """Return the alarm with the given `alarm_id`, or None if no match.

    Match is case-sensitive — `alarm_id` is treated as a stable identifier.
    """
    return _ALARMS_BY_ID.get(alarm_id)


def query_alarms(
    asset_id: str | None = None,
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "start_time",
    sort_order: str = "desc",
) -> tuple[list[Alarm], int]:
    """Return (page of alarms, total matching filter) sorted by `sort_by` and `sort_order`.

    If `asset_id` is given, only alarms for that asset are returned. Sorting is stable;
    original insertion order is the tiebreaker.
    """
    filtered = [alarm for alarm in ALARMS if asset_id is None or alarm.asset_id == asset_id]
    reverse = sort_order == "desc"
    filtered.sort(key=lambda alarm: getattr(alarm, sort_by), reverse=reverse)
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    return filtered[start:end], total