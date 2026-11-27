"""Shared test fixtures.

The application is exercised in-process through Starlette's ``TestClient``: no
server, no ports, no network. Each test gets a clean in-memory session store so
tests do not depend on each other's leftovers.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.sessions import get_session_service


@pytest.fixture
def client() -> Iterator[TestClient]:
    get_session_service().reset()
    # Using TestClient as a context manager runs the app's lifespan hooks.
    with TestClient(app) as test_client:
        yield test_client
