"""T02: prueba de contrato mínimo y protección de datos del health check."""

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_returns_status_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_is_public_without_login():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "www-authenticate" not in response.headers


def test_health_does_not_claim_ai_or_catalog_availability():
    response = client.get("/api/health")
    assert set(response.json()) == {"status"}
