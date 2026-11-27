"""Tests for the session endpoints and the target-URL policy.

These cover the four behaviours Day 2 promises:

1. A valid request creates a session and returns it.
2. A malformed body is rejected with 422 before any service code runs.
3. A syntactically valid but forbidden target is refused with 400.
4. A missing session is a 404 with the standard ``{"detail": ...}`` body.
"""

from fastapi.testclient import TestClient

from app.core.config import settings

SESSIONS_URL = f"{settings.API_PREFIX}/sessions"

PUBLIC_TARGET = "https://example.com/checkout"
OBJECTIVE = "A logged-in user can add an item to the cart and reach checkout"


def test_create_session_returns_created_session(client: TestClient) -> None:
    response = client.post(SESSIONS_URL, json={"url": PUBLIC_TARGET, "objective": OBJECTIVE})

    assert response.status_code == 201
    body = response.json()
    assert body["url"] == PUBLIC_TARGET
    assert body["objective"] == OBJECTIVE
    assert body["status"] == "created"
    assert body["id"]
    assert body["created_at"] == body["updated_at"]
    # Defaults come from the server, not from the client.
    assert body["limits"] == {"max_steps": 20, "max_duration_seconds": 300}


def test_client_cannot_set_server_owned_fields(client: TestClient) -> None:
    response = client.post(
        SESSIONS_URL,
        json={
            "url": PUBLIC_TARGET,
            "objective": OBJECTIVE,
            "status": "completed",  # unknown field: rejected, not silently ignored
        },
    )

    assert response.status_code == 422


def test_created_session_can_be_retrieved(client: TestClient) -> None:
    created = client.post(SESSIONS_URL, json={"url": PUBLIC_TARGET, "objective": OBJECTIVE}).json()

    response = client.get(f"{SESSIONS_URL}/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_unknown_session_returns_404_detail(client: TestClient) -> None:
    response = client.get(f"{SESSIONS_URL}/b3f1c2d4-0000-4000-8000-000000000000")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_sessions_is_newest_first(client: TestClient) -> None:
    first = client.post(SESSIONS_URL, json={"url": PUBLIC_TARGET, "objective": OBJECTIVE}).json()
    second = client.post(
        SESSIONS_URL, json={"url": "https://example.org/signup", "objective": OBJECTIVE}
    ).json()

    response = client.get(SESSIONS_URL)

    assert response.status_code == 200
    ids = [item["id"] for item in response.json()]
    assert ids == [second["id"], first["id"]]


def test_invalid_url_is_rejected_with_422(client: TestClient) -> None:
    response = client.post(SESSIONS_URL, json={"url": "not-a-url", "objective": OBJECTIVE})

    assert response.status_code == 422


def test_unsupported_scheme_is_rejected_with_422(client: TestClient) -> None:
    response = client.post(
        SESSIONS_URL, json={"url": "file:///etc/passwd", "objective": OBJECTIVE}
    )

    assert response.status_code == 422


def test_objective_too_short_is_rejected_with_422(client: TestClient) -> None:
    response = client.post(SESSIONS_URL, json={"url": PUBLIC_TARGET, "objective": "test it"})

    assert response.status_code == 422


def test_private_ip_target_is_refused_with_400(client: TestClient) -> None:
    response = client.post(
        SESSIONS_URL, json={"url": "http://192.168.1.10/admin", "objective": OBJECTIVE}
    )

    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]


def test_loopback_target_is_refused_with_400(client: TestClient) -> None:
    response = client.post(
        SESSIONS_URL, json={"url": "http://127.0.0.1:8000/docs", "objective": OBJECTIVE}
    )

    assert response.status_code == 400


def test_localhost_name_is_refused_with_400(client: TestClient) -> None:
    response = client.post(
        SESSIONS_URL, json={"url": "http://localhost:5174", "objective": OBJECTIVE}
    )

    assert response.status_code == 400


def test_credentials_in_url_are_refused_with_400(client: TestClient) -> None:
    response = client.post(
        SESSIONS_URL,
        json={"url": "https://user:secret@example.com/login", "objective": OBJECTIVE},
    )

    assert response.status_code == 400
    assert "credentials" in response.json()["detail"]


def test_limits_can_be_tightened_but_not_exceeded(client: TestClient) -> None:
    tightened = client.post(
        SESSIONS_URL,
        json={"url": PUBLIC_TARGET, "objective": OBJECTIVE, "limits": {"max_steps": 5}},
    )
    exceeded = client.post(
        SESSIONS_URL,
        json={"url": PUBLIC_TARGET, "objective": OBJECTIVE, "limits": {"max_steps": 500}},
    )

    assert tightened.status_code == 201
    assert tightened.json()["limits"]["max_steps"] == 5
    assert tightened.json()["limits"]["max_duration_seconds"] == 300
    assert exceeded.status_code == 422


def test_openapi_documents_session_endpoints(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    assert SESSIONS_URL in schema["paths"]
    assert f"{SESSIONS_URL}/{{session_id}}" in schema["paths"]
