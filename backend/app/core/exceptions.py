"""Domain exceptions.

These describe *expected* failures in business terms (a bad target, a missing
session) rather than as HTTP errors. Each one carries the status code the API
should answer with, so the handler in ``app/api/errors.py`` stays a single line.

Unexpected exceptions are deliberately not covered — those should surface as 500s
and be visible, not be disguised as normal API behaviour.
"""

from uuid import UUID


class AppError(Exception):
    """Base class for expected, user-facing application errors.

    Defaults to 400: "the request was understood but refused".
    """

    status_code: int = 400


class InvalidTargetError(AppError):
    """The target URL is well-formed but is not allowed by the security policy."""


class SessionNotFoundError(AppError):
    """No session exists with the requested id."""

    status_code = 404

    def __init__(self, session_id: UUID) -> None:
        super().__init__(f"Session '{session_id}' was not found.")
