# services/alarm_service.py — Alarm business logic: list, analytics, priority scoring.

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends

from alarm_api.models import Alarm, TimeRange
from alarm_api.repositories.alarm_repository import (
    AlarmRepository,
    get_alarm_repository,
)


_SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}
_SEVERITY_WEIGHT = {"critical": 40, "high": 30, "medium": 20, "low": 10}
_PRIORITY_WEIGHT = {1: 30, 2: 20, 3: 10, 4: 5}


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


class AlarmService:
    """Aggregations, trend analysis, correlation, flood detection, rationalization, priority."""

    def __init__(self, repo: AlarmRepository) -> None:
        self._repo = repo

    def get_by_id(self, alarm_id: str) -> Alarm | None:
        return self._repo.get_by_id(alarm_id)

    def paginated_list(
        self,
        asset_id: str | None,
        page: int,
        page_size: int,
        sort_by: str,
        sort_order: str,
    ) -> tuple[list[Alarm], int]:
        return self._repo.paginated(
            asset_id=asset_id,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def filter(
        self,
        asset_ids: list[str] | None = None,
        time_range: TimeRange | None = None,
        severity: list[str] | None = None,
        unit: str | None = None,
    ) -> list[Alarm]:
        """Return alarms matching all provided filters (None filter = no filter)."""
        return self._repo.filter(
            asset_ids=asset_ids,
            time_range=time_range,
            severity=severity,
            unit=unit,
        )

    def summarize(
        self,
        asset_ids: list[str] | None,
        time_range: TimeRange | None,
        severity: list[str] | None,
        group_by: list[str] | None,
        kpis: list[str] | None,
    ) -> tuple[list[dict[str, object]], int]:
        """Group filtered alarms by `group_by` and compute requested KPIs."""
        group_by = group_by if group_by is not None else ["alarm_name"]
        kpis = kpis if kpis is not None else ["alarm_count"]
        filtered = self._repo.filter(asset_ids=asset_ids, time_range=time_range, severity=severity)

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

    def trends(
        self,
        asset_ids: list[str] | None,
        time_range: TimeRange | None,
        bucket: str,
        metrics: list[str] | None,
    ) -> list[dict[str, object]]:
        """Bucket filtered alarms by `bucket` and compute requested metrics per bucket."""
        metrics = metrics if metrics is not None else ["alarm_count"]
        filtered = self._repo.filter(asset_ids=asset_ids, time_range=time_range)
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

    def correlations(
        self,
        asset_ids: list[str] | None,
        time_range: TimeRange | None,
        lag_window_minutes: int,
        severity_threshold: str,
        min_support: int,
    ) -> tuple[list[dict[str, object]], int]:
        """Find pairs of distinct alarm_names that activate within `lag_window_minutes`."""
        threshold_rank = _SEVERITY_RANK[severity_threshold]
        filtered = self._repo.filter(asset_ids=asset_ids, time_range=time_range)
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
        self,
        unit: str,
        time_range: TimeRange | None,
        threshold_count: int,
        rolling_window_minutes: int,
    ) -> tuple[list[dict[str, object]], int]:
        """Bin alarms for `unit` into 1-minute buckets; flood if count >= threshold_count."""
        filtered = self._repo.filter(time_range=time_range, unit=unit)
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

    def rationalization_candidates(
        self,
        asset_ids: list[str] | None,
        time_range: TimeRange | None,
        recurrence_threshold: int,
        stale_minutes_threshold: int,
    ) -> list[dict[str, object]]:
        """Surface chattering or stale alarms as rationalization candidates."""
        filtered = self._repo.filter(asset_ids=asset_ids, time_range=time_range)
        candidates: list[dict[str, object]] = []

        # Chattering: same (alarm_name, asset_id) appears >= recurrence_threshold times.
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

        # Stale: state == "active" AND (now - start_time) > stale_minutes_threshold.
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

    def priority_score(
        self, alarm: Alarm
    ) -> tuple[float, str, dict[str, float | int | str]]:
        """Combine severity, configured priority, age, and acknowledgement state."""
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


def get_alarm_service(
    repo: Annotated[AlarmRepository, Depends(get_alarm_repository)],
) -> AlarmService:
    """FastAPI dependency that constructs an AlarmService with the singleton repository."""
    return AlarmService(repo)