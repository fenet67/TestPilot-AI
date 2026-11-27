"""Aggregates every versioned API router behind a single import.

New resources (test cases, reports) are registered here on the day they are
implemented, so ``main.py`` never changes again.
"""

from fastapi import APIRouter

from app.api.routes import health, sessions

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(sessions.router)
