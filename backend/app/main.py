"""FastAPI application entry point.

Run from the ``backend/`` directory:

    .venv/Scripts/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Startup/shutdown hooks.

    Day 1: nothing to start. Later days open the database pool (Day 6) and the
    Playwright browser (Day 3) here, and close them on shutdown — so resources
    are created once per process instead of once per request.
    """
    yield


def create_app() -> FastAPI:
    """Application factory.

    Using a factory keeps the app importable and testable: tests can build a
    fresh instance, and configuration is read explicitly instead of at import
    side-effect time.
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Autonomous AI-powered software testing agent.",
        lifespan=lifespan,
    )

    # The frontend runs on a different origin (port 5173), so the browser needs
    # explicit permission to call this API. Origins come from configuration,
    # never from a wildcard.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix=settings.API_PREFIX)
    return application


app = create_app()
