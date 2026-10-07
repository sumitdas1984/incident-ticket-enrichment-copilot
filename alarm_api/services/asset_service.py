# services/asset_service.py — Asset business logic.

from typing import Annotated

from fastapi import Depends

from alarm_api.models import Asset
from alarm_api.repositories.asset_repository import (
    AssetRepository,
    get_asset_repository,
)


class AssetService:
    """Coordinates asset lookup operations. Currently a thin layer over the repository."""

    def __init__(self, repo: AssetRepository) -> None:
        self._repo = repo

    def get_by_id(self, asset_id: str) -> Asset | None:
        """Return the asset with the given `asset_id`, or None if no match."""
        return self._repo.get_by_id(asset_id)

    def search(self, query: str, limit: int, unit: str | None) -> list[Asset]:
        """Return up to `limit` assets whose `name` contains `query` (case-insensitive)."""
        return self._repo.search(query, limit, unit)


def get_asset_service(
    repo: Annotated[AssetRepository, Depends(get_asset_repository)],
) -> AssetService:
    """FastAPI dependency that constructs an AssetService with the singleton repository."""
    return AssetService(repo)