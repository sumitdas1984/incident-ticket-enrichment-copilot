# routes/__init__.py — Aggregator that mounts all sub-routers onto a single FastAPI router.

from fastapi import APIRouter

from alarm_api.routes.alarms import router as alarms_router
from alarm_api.routes.analytics import router as analytics_router
from alarm_api.routes.assets import router as assets_router
from alarm_api.routes.calculations import router as calculations_router
from alarm_api.routes.recommendations import router as recommendations_router
from alarm_api.routes.system import router as system_router


router = APIRouter()
router.include_router(system_router)
router.include_router(assets_router)
router.include_router(alarms_router)
router.include_router(recommendations_router)
router.include_router(calculations_router)
router.include_router(analytics_router)


__all__ = ["router"]