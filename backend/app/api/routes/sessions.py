"""Session endpoints.

Thin by design: parse the request, delegate to the service, return a schema.
No validation policy and no storage logic lives here.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.schemas.session import SessionCreate, SessionResponse
from app.services.sessions import SessionService, get_session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])

SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a testing session",
    description=(
        "Creates a session for a public http(s) URL and a testing objective. "
        "The target is validated but not contacted. Only test sites you own or "
        "have permission to test."
    ),
)
def create_session(payload: SessionCreate, service: SessionServiceDep) -> SessionResponse:
    return service.create_session(payload)


@router.get(
    "",
    response_model=list[SessionResponse],
    summary="List sessions",
    description="Returns all sessions, newest first.",
)
def list_sessions(service: SessionServiceDep) -> list[SessionResponse]:
    return service.list_sessions()


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Get a session",
    description="Returns a single session by id, or 404 if it does not exist.",
    responses={404: {"description": "Session not found"}},
)
def get_session(session_id: UUID, service: SessionServiceDep) -> SessionResponse:
    return service.get_session(session_id)
