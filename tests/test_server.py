import requests


def test_endpoint_root_and_health():
    """Simple endpoint checks for local server.
    These are integration-style checks that expect a local server to be running on port 8000.
    """
    root_url = "http://localhost:8000/"
    health_url = "http://localhost:8000/health"

    try:
        r1 = requests.get(root_url, timeout=5)
        assert r1.status_code == 200
    except Exception:
        # If server not running, fail the test clearly
        assert False, f"Failed to reach {root_url}"

    try:
        r2 = requests.get(health_url, timeout=5)
        assert r2.status_code == 200
    except Exception:
        assert False, f"Failed to reach {health_url}"
