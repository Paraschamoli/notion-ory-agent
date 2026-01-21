from fastapi import APIRouter, Depends
from src.api.dependencies import SettingsDep
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.config.settings import Settings

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check(settings: SettingsDep):
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "environment": settings.environment,
        "debug": settings.debug
    }

@router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes/Docker health probes."""
    # In the future, we'll add checks for Ory services and Notion
    return {"status": "ready"}

@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes/Docker health probes."""
    return {"status": "alive"}