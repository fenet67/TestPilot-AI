"""Liveness endpoint.

Kept dependency-free on purpose: if this responds, the process is alive and
serving HTTP. Deeper checks (database, browser engine, LLM) get their own
endpoints when those components exist.
"""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["system"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Returns the service status, version and environment. Used by the frontend and by monitoring.",
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )
