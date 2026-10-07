# services/recommendation_service.py — Operator-action recommendations and related/historical context.

from alarm_api.models import Alarm, Asset
from alarm_api.repositories.alarm_repository import AlarmRepository
from alarm_api.repositories.asset_repository import AssetRepository


def _next_action_id(actions: list[dict[str, object]]) -> str:
    return f"ACT-{len(actions) + 1:03d}"


class RecommendationService:
    """Build operator-action recommendations and surface related/historical/asset context."""

    def __init__(self, alarm_repo: AlarmRepository, asset_repo: AssetRepository) -> None:
        self._alarm_repo = alarm_repo
        self._asset_repo = asset_repo

    def get_alarm_by_id(self, alarm_id: str) -> Alarm | None:
        """Return the alarm with the given `alarm_id`, or None if no match."""
        return self._alarm_repo.get_by_id(alarm_id)

    def build_operator_actions(
        self,
        alarm: Alarm,
        related_count: int,
        historical_count: int,
    ) -> list[dict[str, object]]:
        """Build a deterministic list of recommended operator actions for `alarm`."""
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

    def related_alarms(self, alarm: Alarm, lag_minutes: int = 60) -> list[Alarm]:
        return self._alarm_repo.find_related(alarm, lag_minutes)

    def historical_alarms(self, alarm: Alarm) -> list[Alarm]:
        return self._alarm_repo.find_historical(alarm)

    def historical_pattern(self, alarm: Alarm) -> dict[str, object]:
        """Return a summary of historical occurrences of `alarm.alarm_name`."""
        matching = self.historical_alarms(alarm)
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

    def asset_context(self, asset: Asset) -> dict[str, object]:
        """Return the asset-context block for an Operator Actions response."""
        active_count = self._alarm_repo.count_active_for_asset(asset.asset_id)
        return {
            "asset_id": asset.asset_id,
            "name": asset.name,
            "unit": asset.unit,
            "site": asset.site,
            "asset_type": asset.asset_type,
            "active_alarm_count": active_count,
        }