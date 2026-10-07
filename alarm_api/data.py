# data.py — deterministic seed data
# This contains our initial fake industrial data.

from alarm_api.models import Asset


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