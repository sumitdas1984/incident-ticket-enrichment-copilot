# services/calculation_service.py — Generate and execute calculation records.

from datetime import datetime

from alarm_api.models import TimeRange
from alarm_api.repositories.calculation_repository import CalculationRepository
from alarm_api.services.alarm_service import AlarmService, _avg_ack_delay_seconds


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


class CalculationService:
    """Generate and execute calculations, delegating aggregation to AlarmService."""

    def __init__(
        self,
        calc_repo: CalculationRepository,
        alarm_service: AlarmService,
    ) -> None:
        self._calc_repo = calc_repo
        self._alarm_service = alarm_service

    def generate(
        self, calculation_type: str, filters: dict[str, str]
    ) -> dict[str, object]:
        """Create a new calculation record and return its config (including the new ID)."""
        calc_id = f"CALC-{len(self._calc_repo) + 1:04d}"
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
        self._calc_repo.insert(calc_id, record)
        return record

    def execute(
        self, calculation_id: str, override_filters: dict[str, str] | None = None
    ) -> dict[str, object] | None:
        """Run the calculation referenced by `calculation_id`. None if unknown."""
        record = self._calc_repo.get(calculation_id)
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
            return self._execute_flood_index(calculation_id, calc_type, unit, time_range)
        if calc_type == "alarm_count":
            return self._execute_alarm_count(calculation_id, calc_type, asset_ids, time_range)
        if calc_type == "avg_ack_delay_seconds":
            return self._execute_avg_ack_delay(calculation_id, calc_type, asset_ids, time_range)
        if calc_type == "avg_priority":
            return self._execute_avg_priority(calculation_id, calc_type, asset_ids, time_range)
        return {
            "calculation_id": calculation_id,
            "calculation_type": calc_type,
            "result": {"error": f"unsupported calculation_type: {calc_type!r}"},
        }

    def _execute_flood_index(
        self,
        calculation_id: str,
        calc_type: str,
        unit: str | None,
        time_range: TimeRange | None,
    ) -> dict[str, object]:
        if not unit:
            return {
                "calculation_id": calculation_id,
                "calculation_type": calc_type,
                "result": {"error": "filters.unit is required for alarm_flood_index"},
            }
        windows, flood_count = self._alarm_service.detect_floods(
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

    def _execute_alarm_count(
        self,
        calculation_id: str,
        calc_type: str,
        asset_ids: list[str] | None,
        time_range: TimeRange | None,
    ) -> dict[str, object]:
        filtered = self._alarm_service.filter(asset_ids=asset_ids, time_range=time_range)
        return {
            "calculation_id": calculation_id,
            "calculation_type": calc_type,
            "result": {"count": len(filtered)},
        }

    def _execute_avg_ack_delay(
        self,
        calculation_id: str,
        calc_type: str,
        asset_ids: list[str] | None,
        time_range: TimeRange | None,
    ) -> dict[str, object]:
        filtered = self._alarm_service.filter(asset_ids=asset_ids, time_range=time_range)
        avg_delay = _avg_ack_delay_seconds(filtered)
        return {
            "calculation_id": calculation_id,
            "calculation_type": calc_type,
            "result": {
                "avg_ack_delay_seconds": round(avg_delay, 2),
                "sample_size": sum(1 for a in filtered if a.acknowledged_at is not None),
            },
        }

    def _execute_avg_priority(
        self,
        calculation_id: str,
        calc_type: str,
        asset_ids: list[str] | None,
        time_range: TimeRange | None,
    ) -> dict[str, object]:
        filtered = self._alarm_service.filter(asset_ids=asset_ids, time_range=time_range)
        priorities = [a.priority for a in filtered if a.priority is not None]
        avg = sum(priorities) / len(priorities) if priorities else 0.0
        return {
            "calculation_id": calculation_id,
            "calculation_type": calc_type,
            "result": {"avg_priority": round(avg, 2), "sample_size": len(priorities)},
        }