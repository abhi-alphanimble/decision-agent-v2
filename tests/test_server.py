import requests
from fastapi.testclient import TestClient
from app.main import app


def test_endpoint_root_and_health():
    """Simple endpoint checks for local server.
    Try HTTP requests to a running server on port 8000; if connection fails,
    fall back to using FastAPI TestClient directly against the app to keep
    tests hermetic in CI/developer environments.
    """
    root_url = "http://localhost:8000/"
    health_url = "http://localhost:8000/health"

    try:
        r1 = requests.get(root_url, timeout=2)
        assert r1.status_code == 200
        r2 = requests.get(health_url, timeout=2)
        assert r2.status_code == 200
    except Exception:
        # Fall back to TestClient when an external server is not available
        client = TestClient(app)
        r1 = client.get("/")
        assert r1.status_code == 200
        r2 = client.get("/health")
        assert r2.status_code == 200
