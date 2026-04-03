from fastapi.testclient import TestClient

from app.main import app


def test_cors_preflight_should_allow_login_request() -> None:
    client = TestClient(app)

    response = client.options(
        "/api/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "*"
