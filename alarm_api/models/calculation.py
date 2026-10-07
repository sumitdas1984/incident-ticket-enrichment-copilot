# models/calculation.py — Calculation-code generation and execution models

from pydantic import BaseModel, Field


class GenerateCalculationRequest(BaseModel):
    calculation_type: str = Field(
        ...,
        min_length=1,
        description="Type of calculation to generate (e.g. 'alarm_flood_index', 'alarm_count').",
    )
    filters: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Filters persisted with the calculation and applied at execute time. "
            "Recognised keys: unit, asset_ids (comma-separated), start_time, end_time."
        ),
    )


class GenerateCalculationResponse(BaseModel):
    calculation_id: str = Field(..., description="Unique ID used by /calculation-code/execute.")
    calculation_type: str
    filters: dict[str, str]
    code: str = Field(..., description="Human-readable description of what the calculation does.")


class ExecuteCalculationRequest(BaseModel):
    calculation_id: str = Field(..., min_length=1)
    filters: dict[str, str] = Field(
        default_factory=dict,
        description="Optional override filters merged on top of the stored filters.",
    )


class ExecuteCalculationResponse(BaseModel):
    calculation_id: str
    calculation_type: str
    result: dict[str, float | int | str] = Field(
        ...,
        description="Computed metrics. Shape depends on the calculation_type.",
    )