# repositories/calculation_repository.py — In-memory store for generated calculations.

from typing import Any


class CalculationRepository:
    """Persistent store for generated calculations (in-memory, lost on restart)."""

    def __init__(self) -> None:
        self._records: dict[str, dict[str, Any]] = {}

    def insert(self, calc_id: str, record: dict[str, Any]) -> dict[str, Any]:
        """Persist `record` under `calc_id` and return the stored record."""
        self._records[calc_id] = record
        return record

    def get(self, calc_id: str) -> dict[str, Any] | None:
        """Return the calculation record for `calc_id`, or None if not found."""
        return self._records.get(calc_id)

    def __len__(self) -> int:
        """Return the number of stored calculation records."""
        return len(self._records)


# Module-level singleton — empty at boot, populated by CalculationService.generate.
calculation_repository = CalculationRepository()


def get_calculation_repository() -> CalculationRepository:
    """FastAPI dependency that yields the singleton calculation repository."""
    return calculation_repository