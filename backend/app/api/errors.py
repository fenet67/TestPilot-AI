"""Translates domain errors into HTTP responses.

One handler, registered once, so routes have no ``try/except`` blocks and every
error keeps FastAPI's standard body shape: ``{"detail": "..."}``.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError


def register_exception_handlers(app: FastAPI) -> None:
    """Map every expected application error to a JSON response.

    Starlette resolves handlers by the exception's MRO, so this one handler covers
    all ``AppError`` subclasses. Each subclass already carries its own status code,
    so nothing is mapped twice.
    """

    @app.exception_handler(AppError)
    async def handle_app_error(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})
