"""Schemas for the system health endpoint."""

from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Shape of ``GET /api/v1/health``.

    Declaring this as a model means the endpoint's response is validated on the
    way out and documented in OpenAPI (Swagger UI) automatically.
    """

    status: Literal["ok", "degraded"] = Field(description="Overall service status.")
    service: str = Field(description="Human-readable service name.")
    version: str = Field(description="Running application version.")
    environment: str = Field(description="Deployment environment name.")
