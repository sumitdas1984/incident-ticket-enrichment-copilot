# repositories/alarm_repository.py — In-memory alarm data access.

from datetime import timedelta

from alarm_api.data import ALARMS
from alarm_api.models import Alarm, TimeRange


class AlarmRepository:
    """Lookup, query, filter, and correlation-supporting operations for the alarm seed."""

    def __init__(self, alarms: list[Alarm]) -> None:
        self._alarms = list(alarms)
        self._by_id: dict[str, Alarm] = {alarm.alarm_id: alarm for alarm in self._alarms}

    def get_by_id(self, alarm_id: str) -> Alarm | None:
        """Return the alarm with the given `alarm_id`, or None if no match."""
        return self._by_id.get(alarm_id)

    def paginated(
        self,
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
        filtered = [alarm for alarm in self._alarms if asset_id is None or alarm.asset_id == asset_id]
        reverse = sort_order == "desc"
        filtered.sort(key=lambda alarm: getattr(alarm, sort_by), reverse=reverse)
        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        return filtered[start:end], total

    def filter(
        self,
        asset_ids: list[str] | None = None,
        time_range: TimeRange | None = None,
        severity: list[str] | None = None,
        unit: str | None = None,
    ) -> list[Alarm]:
        """Return alarms matching all provided filters (None filter = no filter)."""
        filtered = list(self._alarms)
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

    def find_related(self, alarm: Alarm, lag_minutes: int = 60) -> list[Alarm]:
        """Return other alarms on the same asset activated within ±`lag_minutes` of `alarm`."""
        lag = timedelta(minutes=lag_minutes)
        cutoff_low = alarm.start_time - lag
        cutoff_high = alarm.start_time + lag
        related: list[Alarm] = [
            other
            for other in self._alarms
            if other.alarm_id != alarm.alarm_id
            and other.asset_id == alarm.asset_id
            and cutoff_low <= other.start_time <= cutoff_high
        ]
        related.sort(key=lambda a: a.start_time)
        return related

    def find_historical(self, alarm: Alarm) -> list[Alarm]:
        """Return historical Alarm objects with the same `alarm_name` (excluding self)."""
        return [
            a
            for a in self._alarms
            if a.alarm_name == alarm.alarm_name and a.alarm_id != alarm.alarm_id
        ]

    def count_active_for_asset(self, asset_id: str) -> int:
        """Return the count of currently-`active` alarms for the given asset_id."""
        return sum(1 for a in self._alarms if a.asset_id == asset_id and a.state == "active")


# Module-level singleton wired to the deterministic seed.
alarm_repository = AlarmRepository(ALARMS)


def get_alarm_repository() -> AlarmRepository:
    """FastAPI dependency that yields the singleton alarm repository."""
    return alarm_repository