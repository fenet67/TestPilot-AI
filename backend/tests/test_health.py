"""Tests for the health endpoint.

These run against the ASGI app in-process via starlette's TestClient — no
server, no network, no port conflicts.
"""

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get(f"{settings.API_PREFIX}/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == settings.PROJECT_NAME
    assert body["version"] == settings.VERSION
    assert body["environment"] == settings.ENVIRONMENT


def test_unknown_route_returns_404() -> None:
    response = client.get(f"{settings.API_PREFIX}/does-not-exist")

    assert response.status_code == 404
