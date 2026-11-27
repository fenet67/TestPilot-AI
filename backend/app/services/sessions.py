"""Session service — the only place that creates or reads sessions.

Storage is an in-memory dict for now. That is a deliberate stand-in, not a design:
Day 6 replaces the body of this class with PostgreSQL via SQLAlchemy. Because the
routes and schemas depend on this service and not on a dict, that swap will not
touch ``api/`` or ``schemas/``.

Concurrency: FastAPI runs sync endpoints in a thread pool, so two requests really
can hit this object at once. A ``Lock`` around the dict is the minimum correct
thing; a database transaction will play the same role later.
"""

from datetime import UTC, datetime
from threading import Lock
from uuid import UUID, uuid4

from app.core.exceptions import SessionNotFoundError
from app.core.url_policy import assert_target_is_allowed
from app.schemas.session import SessionCreate, SessionResponse, SessionStatus


class SessionService:
    """Creates, stores and retrieves testing sessions."""

    def __init__(self) -> None:
        self._sessions: dict[UUID, SessionResponse] = {}
        self._lock = Lock()

    def create_session(self, payload: SessionCreate) -> SessionResponse:
        """Validate the target and persist a new session in the ``created`` state.

        The URL is checked here rather than in the schema because "not allowed by
        policy" is a refusal (400), not a malformed request (422). No network call
        happens yet — creating a session never touches the target.
        """
        assert_target_is_allowed(payload.url)

        now = datetime.now(UTC)
        session = SessionResponse(
            id=uuid4(),
            url=str(payload.url),
            objective=payload.objective,
            status=SessionStatus.CREATED,
            limits=payload.limits,
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self._sessions[session.id] = session
        return session

    def get_session(self, session_id: UUID) -> SessionResponse:
        with self._lock:
            session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)
        return session

    def list_sessions(self) -> list[SessionResponse]:
        """All sessions, newest first."""
        with self._lock:
            sessions = list(self._sessions.values())
        return sorted(sessions, key=lambda item: item.created_at, reverse=True)

    def reset(self) -> None:
        """Drop all sessions. Test helper; removed once Day 6 adds the database."""
        with self._lock:
            self._sessions.clear()


_service = SessionService()


def get_session_service() -> SessionService:
    """FastAPI dependency.

    Indirection through a function lets tests override the dependency, and lets
    Day 6 return a repository-backed service instead of a new one.
    """
    return _service
