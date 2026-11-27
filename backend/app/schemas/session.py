"""Schemas for testing sessions.

A *session* is one unit of work: "test this URL against this objective, under
these limits". It is the aggregate everything else hangs off (plans, test cases,
executions, evidence), so its contract is defined carefully and early.

Request and response models are separate on purpose. ``SessionCreate`` is what a
client may send; ``SessionResponse`` is what the server owns. A client cannot set
its own ``id``, ``status`` or timestamps by adding fields to the payload.
"""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class SessionStatus(StrEnum):
    """Lifecycle states of a session.

    Day 2 only ever produces ``created``. The remaining values exist so the
    contract does not break when the agent starts moving sessions through them.
    """

    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SessionLimits(BaseModel):
    """Hard, server-enforced budgets for a run.

    Defaults are chosen so a single session cannot run up an unbounded bill or
    hang forever; clients may request stricter limits, not looser ones.
    """

    max_steps: int = Field(default=20, ge=1, le=50, description="Maximum agent steps.")
    max_duration_seconds: int = Field(
        default=300, ge=10, le=1800, description="Wall-clock budget for the run."
    )


class SessionCreate(BaseModel):
    """Body of ``POST /api/v1/sessions``."""

    # extra="forbid" turns a typo like "objectiv" into a 422 instead of a silently
    # ignored field — the failure mode you actually want on a public API.
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    url: HttpUrl = Field(description="Public http(s) URL to test.")
    objective: str = Field(
        min_length=10,
        max_length=500,
        description=(
            "What should be verified, e.g. 'A valid user can register "
            "and land on the dashboard'."
        ),
    )
    limits: SessionLimits = Field(default_factory=SessionLimits)


class SessionResponse(BaseModel):
    """A stored session, as returned by the API."""

    id: UUID
    url: str = Field(description="Normalized target URL.")
    objective: str
    status: SessionStatus
    limits: SessionLimits
    created_at: datetime
    updated_at: datetime
