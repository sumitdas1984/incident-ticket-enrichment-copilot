# routes/system.py — Liveness and readiness endpoints.

from fastapi import APIRouter


router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}