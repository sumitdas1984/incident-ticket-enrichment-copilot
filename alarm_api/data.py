# data.py — deterministic seed data
# This contains our initial fake industrial data.

from datetime import UTC, datetime, timedelta, timezone

from alarm_api.models import Alarm, Asset, KpiDefinition, TimeRange


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


# ----- Phase 4: analytics helpers -----


def filter_alarms(
    asset_ids: list[str] | None = None,
    time_range: TimeRange | None = None,
    severity: list[str] | None = None,
    unit: str | None = None,
) -> list[Alarm]:
    """Return alarms matching all provided filters (None filter = no filter)."""
    filtered = list(ALARMS)
    if asset_ids is not None:
        asset_set = set(asset_ids)
        filtered = [a for a in filtered if a.asset_id in asset_set]
    if time_range is not None:
        filtered = [
            a
            for a in filtered
            if time_range.start_time <= a.start_time <= time_range.end_time
        ]
    if severity is not None:
        sev_set = set(severity)
        filtered = [a for a in filtered if a.severity in sev_set]
    if unit is not None:
        filtered = [a for a in filtered if a.unit == unit]
    return filtered


def _bucket_start(t: datetime, freq: str) -> datetime:
    """Return the start-of-bucket datetime for the given frequency."""
    if freq == "hourly":
        return t.replace(minute=0, second=0, microsecond=0)
    if freq == "daily":
        return t.replace(hour=0, minute=0, second=0, microsecond=0)
    if freq == "weekly":
        days_since_monday = t.weekday()
        start = t - timedelta(days=days_since_monday)
        return start.replace(hour=0, minute=0, second=0, microsecond=0)
    raise ValueError(f"unknown bucket frequency: {freq}")


def _avg_ack_delay_seconds(alarms_to_measure: list[Alarm]) -> float:
    """Mean (acknowledged_at - start_time) in seconds over alarms that have been acknowledged."""
    delays: list[float] = [
        (a.acknowledged_at - a.start_time).total_seconds()
        for a in alarms_to_measure
        if a.acknowledged_at is not None
    ]
    return sum(delays) / len(delays) if delays else 0.0


def summarize_alarms(
    asset_ids: list[str] | None = None,
    time_range: TimeRange | None = None,
    severity: list[str] | None = None,
    group_by: list[str] | None = None,
    kpis: list[str] | None = None,
) -> tuple[list[dict[str, object]], int]:
    """Group filtered alarms by `group_by` and compute requested KPIs."""
    group_by = group_by if group_by is not None else ["alarm_name"]
    kpis = kpis if kpis is not None else ["alarm_count"]
    filtered = filter_alarms(asset_ids=asset_ids, time_range=time_range, severity=severity)

    groups: dict[tuple[tuple[str, str], ...], list[Alarm]] = {}
    for alarm in filtered:
        key = tuple((field, str(getattr(alarm, field, ""))) for field in group_by)
        groups.setdefault(key, []).append(alarm)

    result: list[dict[str, object]] = []
    for key_tuple, items in groups.items():
        metrics: dict[str, float | int] = {}
        if "alarm_count" in kpis:
            metrics["alarm_count"] = len(items)
        if "recurring_rate" in kpis:
            name_counts: dict[str, int] = {}
            for item in items:
                name_counts[item.alarm_name] = name_counts.get(item.alarm_name, 0) + 1
            recurring = sum(1 for c in name_counts.values() if c > 1)
            metrics["recurring_rate"] = round(recurring / len(items), 4) if items else 0.0
        if "avg_ack_delay_seconds" in kpis:
            metrics["avg_ack_delay_seconds"] = round(_avg_ack_delay_seconds(items), 2)
        result.append({"key": dict(key_tuple), "metrics": metrics})

    return result, len(filtered)


def compute_alarm_trends(
    asset_ids: list[str] | None = None,
    time_range: TimeRange | None = None,
    bucket: str = "daily",
    metrics: list[str] | None = None,
) -> list[dict[str, object]]:
    """Bucket filtered alarms by `bucket` and compute requested metrics per bucket."""
    metrics = metrics if metrics is not None else ["alarm_count"]
    filtered = filter_alarms(asset_ids=asset_ids, time_range=time_range)
    buckets: dict[str, list[Alarm]] = {}
    for alarm in filtered:
        b_start = _bucket_start(alarm.start_time, bucket)
        buckets.setdefault(b_start.isoformat(), []).append(alarm)

    out: list[dict[str, object]] = []
    for b_iso in sorted(buckets):
        items = buckets[b_iso]
        m: dict[str, float | int] = {}
        if "alarm_count" in metrics:
            m["alarm_count"] = len(items)
        if "avg_ack_delay_seconds" in metrics:
            m["avg_ack_delay_seconds"] = round(_avg_ack_delay_seconds(items), 2)
        out.append({"bucket_start": datetime.fromisoformat(b_iso), "metrics": m})
    return out


_SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def compute_correlations(
    asset_ids: list[str] | None = None,
    time_range: TimeRange | None = None,
    lag_window_minutes: int = 15,
    severity_threshold: str = "medium",
    min_support: int = 1,
) -> tuple[list[dict[str, object]], int]:
    """Find pairs of distinct alarm_names that activate within `lag_window_minutes` of each other.

    Filters by severity_threshold (inclusive) before pairing.
    """
    threshold_rank = _SEVERITY_RANK[severity_threshold]
    filtered = filter_alarms(asset_ids=asset_ids, time_range=time_range)
    filtered = [a for a in filtered if _SEVERITY_RANK.get(a.severity, 0) >= threshold_rank]
    filtered.sort(key=lambda a: a.start_time)

    total = len(filtered)
    pair_counts: dict[tuple[str, str], int] = {}
    lag_delta = timedelta(minutes=lag_window_minutes)
    for i, anchor in enumerate(filtered):
        for other in filtered[i + 1 :]:
            if other.start_time - anchor.start_time > lag_delta:
                break
            if other.alarm_name == anchor.alarm_name:
                continue
            a, b = sorted((anchor.alarm_name, other.alarm_name))
            pair_counts[(a, b)] = pair_counts.get((a, b), 0) + 1

    pairs: list[dict[str, object]] = []
    for (a, b), count in sorted(pair_counts.items(), key=lambda kv: -kv[1]):
        if count < min_support:
            continue
        pairs.append(
            {
                "alarm_name_a": a,
                "alarm_name_b": b,
                "cooccurrence_count": count,
                "support": round(count / total, 4) if total else 0.0,
            }
        )
    return pairs, total


def detect_floods(
    unit: str,
    time_range: TimeRange | None = None,
    threshold_count: int = 10,
    rolling_window_minutes: int = 10,
) -> tuple[list[dict[str, object]], int]:
    """Bin alarms for `unit` into 1-minute buckets; a window is a flood if count >= threshold_count."""
    filtered = filter_alarms(time_range=time_range, unit=unit)
    if not filtered:
        return [], 0
    filtered.sort(key=lambda a: a.start_time)
    bins: dict[str, int] = {}
    for alarm in filtered:
        b = alarm.start_time.replace(second=0, microsecond=0)
        bins[b.isoformat()] = bins.get(b.isoformat(), 0) + 1
    windows: list[dict[str, object]] = []
    flood_count = 0
    for b_iso in sorted(bins):
        count = bins[b_iso]
        is_flood = count >= threshold_count
        if is_flood:
            flood_count += 1
        windows.append(
            {
                "window_start": datetime.fromisoformat(b_iso),
                "alarm_count": count,
                "is_flood": is_flood,
            }
        )
    return windows, flood_count


def find_rationalization_candidates(
    asset_ids: list[str] | None = None,
    time_range: TimeRange | None = None,
    recurrence_threshold: int = 5,
    stale_minutes_threshold: int = 180,
) -> list[dict[str, object]]:
    """Return candidates for alarm rationalization: chattering or stale alarms."""
    filtered = filter_alarms(asset_ids=asset_ids, time_range=time_range)
    candidates: list[dict[str, object]] = []

    # Chattering: same (alarm_name, asset_id) appears more than `recurrence_threshold` times.
    counts: dict[tuple[str, str], int] = {}
    for alarm in filtered:
        key = (alarm.alarm_name, alarm.asset_id)
        counts[key] = counts.get(key, 0) + 1
    for (name, asset_id), count in counts.items():
        if count >= recurrence_threshold:
            candidates.append(
                {
                    "alarm_name": name,
                    "asset_id": asset_id,
                    "occurrence_count": count,
                    "reason": "chattering",
                }
            )

    # Stale: state == "active" AND (now - start_time) > stale_minutes_threshold minutes.
    now = datetime.now(UTC)
    stale_delta = timedelta(minutes=stale_minutes_threshold)
    for alarm in filtered:
        if alarm.state == "active" and (now - alarm.start_time) > stale_delta:
            candidates.append(
                {
                    "alarm_name": alarm.alarm_name,
                    "asset_id": alarm.asset_id,
                    "occurrence_count": 1,
                    "reason": "stale",
                }
            )

    return candidates


_SEVERITY_WEIGHT = {"critical": 40, "high": 30, "medium": 20, "low": 10}
_PRIORITY_WEIGHT = {1: 30, 2: 20, 3: 10, 4: 5}


def compute_priority_score(alarm: Alarm) -> tuple[float, str, dict[str, float | int | str]]:
    """Compute a simple priority score for a single alarm.

    Combines severity, configured priority, age, and acknowledgement state.
    """
    severity_score = _SEVERITY_WEIGHT.get(alarm.severity, 0)
    priority_score = _PRIORITY_WEIGHT.get(alarm.priority or 0, 0)

    age_hours = (datetime.now(UTC) - alarm.start_time).total_seconds() / 3600
    age_score = round(min(age_hours / 24 * 5, 5), 2)

    if alarm.state == "acknowledged":
        ack_penalty = 10
    elif alarm.state in ("cleared", "resolved"):
        ack_penalty = 20
    else:
        ack_penalty = 0

    total = severity_score + priority_score + age_score - ack_penalty
    if total >= 60:
        band = "critical"
    elif total >= 45:
        band = "high"
    elif total >= 30:
        band = "medium"
    else:
        band = "low"

    factors: dict[str, float | int | str] = {
        "severity_score": severity_score,
        "priority_score": priority_score,
        "age_score": age_score,
        "ack_penalty": -ack_penalty,
        "state": alarm.state,
    }
    return round(total, 2), band, factors


# ----- Phase 5: operator-action recommendations -----


def _next_action_id(actions: list[dict[str, object]]) -> str:
    return f"ACT-{len(actions) + 1:03d}"


def build_operator_actions(
    alarm: Alarm,
    related_count: int,
    historical_count: int,
) -> list[dict[str, object]]:
    """Build a deterministic list of recommended operator actions for `alarm`.

    Only counts are needed — the action text doesn't change based on which ones.
    """
    actions: list[dict[str, object]] = []

    # --- Severity-driven actions ---
    if alarm.severity == "critical":
        actions.append(
            {
                "action_id": _next_action_id(actions),
                "title": "Engage critical-alarm response procedure",
                "description": (
                    f"Critical alarm '{alarm.alarm_name}' is active on "
                    f"{alarm.asset_name or alarm.asset_id}. Follow the site's "
                    "critical-alarm response checklist now."
                ),
                "priority": "critical",
                "rationale": "Severity is 'critical', which mandates immediate escalation.",
                "category": "immediate_response",
            }
        )
        actions.append(
            {
                "action_id": _next_action_id(actions),
                "title": "Notify shift supervisor",
                "description": (
                    "Page the on-shift supervisor with the alarm ID and asset ID."
                ),
                "priority": "high",
                "rationale": "Critical alarms are escalation events.",
                "category": "immediate_response",
            }
        )
    elif alarm.severity == "high":
        actions.append(
            {
                "action_id": _next_action_id(actions),
                "title": "Investigate the asset",
                "description": (
                    f"Inspect {alarm.asset_name or alarm.asset_id} for the cause of "
                    f"'{alarm.alarm_name}'."
                ),
                "priority": "high",
                "rationale": "Severity is 'high', operator investigation required.",
                "category": "investigation",
            }
        )
    elif alarm.severity == "medium":
        actions.append(
            {
                "action_id": _next_action_id(actions),
                "title": "Review the alarm",
                "description": (
                    f"Check whether '{alarm.alarm_name}' is consistent with current operations."
                ),
                "priority": "medium",
                "rationale": "Severity is 'medium', verification required.",
                "category": "investigation",
            }
        )
    # 'low' severity intentionally produces no severity-specific action.

    # --- State-driven actions ---
    if alarm.state == "active":
        actions.append(
            {
                "action_id": _next_action_id(actions),
                "title": "Acknowledge the alarm",
                "description": (
                    f"Acknowledge '{alarm.alarm_name}' on the operator console to "
                    "confirm awareness."
                ),
                "priority": "medium",
                "rationale": f"Alarm is in '{alarm.state}' state.",
                "category": "documentation",
            }
        )

    # --- Related-alarms action ---
    if related_count > 0:
        actions.append(
            {
                "action_id": _next_action_id(actions),
                "title": f"Review {related_count} related alarm(s)",
                "description": (
                    f"{related_count} other alarm(s) recently activated on or near "
                    f"{alarm.asset_id}. Investigate for a shared root cause."
                ),
                "priority": "medium",
                "rationale": "Correlated alarms often share a root cause.",
                "category": "investigation",
            }
        )

    # --- Always: process-review action ---
    actions.append(
        {
            "action_id": _next_action_id(actions),
            "title": "Check related processes",
            "description": (
                f"Review upstream and downstream processes for "
                f"{alarm.asset_name or alarm.asset_id} for related anomalies."
            ),
            "priority": "medium",
            "rationale": "Operating context often surfaces the underlying cause.",
            "category": "investigation",
        }
    )

    # --- Historical playbook (only if this alarm_name has prior history) ---
    if historical_count > 1:
        actions.append(
            {
                "action_id": _next_action_id(actions),
                "title": "Consult historical playbook",
                "description": (
                    f"'{alarm.alarm_name}' has occurred {historical_count} times in the "
                    "seed. Review the historical pattern to anticipate the likely outcome."
                ),
                "priority": "low",
                "rationale": "Recurring alarms benefit from prior response notes.",
                "category": "documentation",
            }
        )

    # --- Always: log ---
    actions.append(
        {
            "action_id": _next_action_id(actions),
            "title": "Log observation in shift journal",
            "description": (
                "Record the alarm response and any actions taken for the shift handover."
            ),
            "priority": "low",
            "rationale": "Maintains operational record.",
            "category": "documentation",
        }
    )

    return actions


def related_alarms_for(alarm: Alarm, lag_minutes: int = 60) -> list[Alarm]:
    """Return other alarms on the same asset that activated within ±`lag_minutes` of `alarm`."""
    lag = timedelta(minutes=lag_minutes)
    cutoff_low = alarm.start_time - lag
    cutoff_high = alarm.start_time + lag
    related: list[Alarm] = [
        other
        for other in ALARMS
        if other.alarm_id != alarm.alarm_id
        and other.asset_id == alarm.asset_id
        and cutoff_low <= other.start_time <= cutoff_high
    ]
    related.sort(key=lambda a: a.start_time)
    return related


def historical_alarms_for(alarm: Alarm) -> list[Alarm]:
    """Return historical Alarm objects with the same `alarm_name` as `alarm` (excluding self)."""
    return [
        a
        for a in ALARMS
        if a.alarm_name == alarm.alarm_name and a.alarm_id != alarm.alarm_id
    ]


def historical_pattern_for(alarm: Alarm) -> dict[str, object]:
    """Return a summary of historical occurrences of `alarm.alarm_name`."""
    matching = historical_alarms_for(alarm)
    occurrence_count = len(matching) + 1  # include the current alarm
    last = max((a.start_time for a in matching), default=None)

    common_actions: list[str] = []
    states = {a.state for a in matching}
    if "acknowledged" in states:
        common_actions.append("Typically acknowledged within 30 minutes")
    if "resolved" in states:
        common_actions.append("Often resolved by asset restart or cycle")
    if "cleared" in states:
        common_actions.append("Self-clears once process returns to normal")
    if not common_actions:
        common_actions.append("No historical resolution pattern in seed data")

    return {
        "alarm_name": alarm.alarm_name,
        "occurrence_count": occurrence_count,
        "last_occurrence": last,
        "common_actions": common_actions,
    }


def asset_context_for(asset: Asset) -> dict[str, object]:
    """Return the asset-context block for an Operator Actions response."""
    active_count = sum(
        1 for a in ALARMS if a.asset_id == asset.asset_id and a.state == "active"
    )
    return {
        "asset_id": asset.asset_id,
        "name": asset.name,
        "unit": asset.unit,
        "site": asset.site,
        "asset_type": asset.asset_type,
        "active_alarm_count": active_count,
    }


# ----- Phase 6: calculation code & KPI definitions -----


def _parse_iso_datetime(s: str | None) -> datetime | None:
    """Parse an ISO-8601 datetime string (with optional trailing 'Z'). Returns None on failure."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _filters_to_time_range(filters: dict[str, str]) -> TimeRange | None:
    start = _parse_iso_datetime(filters.get("start_time"))
    end = _parse_iso_datetime(filters.get("end_time"))
    if start is None or end is None:
        return None
    return TimeRange(start_time=start, end_time=end)


def _filters_to_asset_ids(filters: dict[str, str]) -> list[str] | None:
    raw = filters.get("asset_ids")
    if not raw:
        return None
    ids = [piece.strip() for piece in raw.split(",")]
    return [piece for piece in ids if piece] or None


_CALCULATIONS: dict[str, dict[str, object]] = {}


_CALCULATION_DESCRIPTIONS: dict[str, str] = {
    "alarm_flood_index": (
        "Compute flood_index = flood_windows / total_windows over the filtered alarms."
    ),
    "alarm_count": "Count alarms matching the filters.",
    "avg_ack_delay_seconds": (
        "Mean (acknowledged_at - start_time) in seconds over alarms matching the filters."
    ),
    "avg_priority": "Mean priority value across alarms matching the filters.",
}


def generate_calculation(
    calculation_type: str, filters: dict[str, str]
) -> dict[str, object]:
    """Create a new calculation record and return its config (including the new ID)."""
    calc_id = f"CALC-{len(_CALCULATIONS) + 1:04d}"
    code = _CALCULATION_DESCRIPTIONS.get(
        calculation_type,
        f"No description available for calculation_type={calculation_type!r}.",
    )
    record: dict[str, object] = {
        "calculation_id": calc_id,
        "calculation_type": calculation_type,
        "filters": dict(filters),
        "code": code,
    }
    _CALCULATIONS[calc_id] = record
    return record


def execute_calculation(
    calculation_id: str, override_filters: dict[str, str] | None = None
) -> dict[str, object] | None:
    """Run the calculation referenced by `calculation_id`.

    Returns None if the calculation_id is unknown. `override_filters` are merged on
    top of the stored filters.
    """
    record = _CALCULATIONS.get(calculation_id)
    if record is None:
        return None
    calc_type_obj = record["calculation_type"]
    calc_type = calc_type_obj if isinstance(calc_type_obj, str) else str(calc_type_obj)
    stored_filters_obj = record["filters"]
    stored_filters = (
        dict(stored_filters_obj) if isinstance(stored_filters_obj, dict) else {}
    )
    effective: dict[str, str] = {**stored_filters, **(override_filters or {})}

    time_range = _filters_to_time_range(effective)
    asset_ids = _filters_to_asset_ids(effective)
    unit = effective.get("unit")

    if calc_type == "alarm_flood_index":
        if not unit:
            return {
                "calculation_id": calculation_id,
                "calculation_type": calc_type,
                "result": {"error": "filters.unit is required for alarm_flood_index"},
            }
        windows, flood_count = detect_floods(
            unit=unit,
            time_range=time_range,
            threshold_count=10,
            rolling_window_minutes=10,
        )
        total = len(windows)
        return {
            "calculation_id": calculation_id,
            "calculation_type": calc_type,
            "result": {
                "flood_index": round(flood_count / total, 4) if total else 0.0,
                "flood_windows": flood_count,
                "total_windows": total,
                "unit": unit,
            },
        }
    if calc_type == "alarm_count":
        alarms = filter_alarms(asset_ids=asset_ids, time_range=time_range)
        return {
            "calculation_id": calculation_id,
            "calculation_type": calc_type,
            "result": {"count": len(alarms)},
        }
    if calc_type == "avg_ack_delay_seconds":
        alarms = filter_alarms(asset_ids=asset_ids, time_range=time_range)
        avg_delay = _avg_ack_delay_seconds(alarms)
        return {
            "calculation_id": calculation_id,
            "calculation_type": calc_type,
            "result": {
                "avg_ack_delay_seconds": round(avg_delay, 2),
                "sample_size": sum(1 for a in alarms if a.acknowledged_at is not None),
            },
        }
    if calc_type == "avg_priority":
        alarms = filter_alarms(asset_ids=asset_ids, time_range=time_range)
        priorities = [a.priority for a in alarms if a.priority is not None]
        avg = sum(priorities) / len(priorities) if priorities else 0.0
        return {
            "calculation_id": calculation_id,
            "calculation_type": calc_type,
            "result": {"avg_priority": round(avg, 2), "sample_size": len(priorities)},
        }
    return {
        "calculation_id": calculation_id,
        "calculation_type": calc_type,
        "result": {"error": f"unsupported calculation_type: {calc_type!r}"},
    }


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