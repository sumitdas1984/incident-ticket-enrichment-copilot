# routes/calculations.py — Calculation-code generate/execute endpoints.

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from alarm_api.models import (
    ExecuteCalculationRequest,
    ExecuteCalculationResponse,
    GenerateCalculationRequest,
    GenerateCalculationResponse,
)
from alarm_api.services import CalculationService, get_calculation_service


router = APIRouter(prefix="/calculation-code", tags=["calculations"])


@router.post("/generate", response_model=GenerateCalculationResponse)
def calc_generate(
    req: GenerateCalculationRequest,
    service: Annotated[CalculationService, Depends(get_calculation_service)],
) -> GenerateCalculationResponse:
    """Create a new calculation record and return its ID + persisted config."""
    record = service.generate(req.calculation_type, req.filters)
    return GenerateCalculationResponse(**record)  # type: ignore[arg-type]


@router.post("/execute", response_model=ExecuteCalculationResponse)
def calc_execute(
    req: ExecuteCalculationRequest,
    service: Annotated[CalculationService, Depends(get_calculation_service)],
) -> ExecuteCalculationResponse:
    """Run a previously generated calculation."""
    record = service.execute(req.calculation_id, req.filters)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"calculation {req.calculation_id!r} not found",
        )
    return ExecuteCalculationResponse(
        calculation_id=str(record["calculation_id"]),
        calculation_type=str(record["calculation_type"]),
        result=record["result"],  # type: ignore[arg-type]
    )