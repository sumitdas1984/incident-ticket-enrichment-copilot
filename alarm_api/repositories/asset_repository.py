# repositories/asset_repository.py — In-memory asset data access.

from alarm_api.data import ASSETS
from alarm_api.models import Asset


class AssetRepository:
    """Lookup and search operations for the asset seed."""

    def __init__(self, assets: list[Asset]) -> None:
        self._assets = list(assets)
        self._by_id: dict[str, Asset] = {asset.asset_id: asset for asset in self._assets}

    def get_by_id(self, asset_id: str) -> Asset | None:
        """Return the asset with the given `asset_id`, or None if no match.

        Match is case-sensitive — `asset_id` is treated as a stable identifier.
        """
        return self._by_id.get(asset_id)

    def search(self, query: str, limit: int, unit: str | None) -> list[Asset]:
        """Return up to `limit` assets whose `name` contains `query` (case-insensitive substring).

        If `unit` is given, only assets whose `unit` exactly matches (case-insensitive)
        are returned. Insertion order is preserved.
        """
        needle = query.lower().strip()
        unit_filter = unit.lower().strip() if unit is not None else None

        results: list[Asset] = []
        for asset in self._assets:
            if needle not in asset.name.lower():
                continue
            if unit_filter is not None:
                if asset.unit is None or asset.unit.lower() != unit_filter:
                    continue
            results.append(asset)
            if len(results) >= limit:
                break
        return results


# Module-level singleton wired to the deterministic seed.
asset_repository = AssetRepository(ASSETS)


def get_asset_repository() -> AssetRepository:
    """FastAPI dependency that yields the singleton asset repository."""
    return asset_repository