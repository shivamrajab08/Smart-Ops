from unittest.mock import MagicMock, patch
import requests
from app import app


def test_home():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.content_type
    assert b"Smart Ops Dashboard" in response.data


def test_health():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_test_service_missing_url():
    client = app.test_client()
    response = client.post("/api/test-service", json={})

    assert response.status_code == 400
    assert response.get_json()["success"] is False
    assert "URL parameter is required" in response.get_json()["error"]


def test_test_service_invalid_method():
    client = app.test_client()
    response = client.post("/api/test-service", json={
        "url": "https://example.com",
        "method": "INVALID"
    })

    assert response.status_code == 400
    assert response.get_json()["success"] is False
    assert "Invalid HTTP method" in response.get_json()["error"]


def test_test_service_blocks_localhost():
    client = app.test_client()
    response = client.post("/api/test-service", json={
        "url": "http://localhost:8080/secret"
    })

    assert response.status_code == 400
    assert response.get_json()["success"] is False
    assert "blocked" in response.get_json()["error"].lower()


def test_test_service_blocks_private_ip():
    client = app.test_client()
    response = client.post("/api/test-service", json={
        "url": "http://192.168.1.1/admin"
    })

    assert response.status_code == 400
    assert response.get_json()["success"] is False
    assert "blocked" in response.get_json()["error"].lower()


def test_test_service_invalid_scheme():
    client = app.test_client()
    response = client.post("/api/test-service", json={
        "url": "ftp://example.com/file.txt"
    })

    assert response.status_code == 400
    assert response.get_json()["success"] is False


@patch("requests.request")
def test_test_service_success(mock_request):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.reason = "OK"
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.content = b'{"status": "ok"}'
    mock_resp.text = '{"status": "ok"}'
    mock_request.return_value = mock_resp

    client = app.test_client()
    response = client.post("/api/test-service", json={
        "url": "https://api.example.com/health",
        "method": "GET",
        "expected_status": 200
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["passed"] is True
    assert data["status_code"] == 200
    assert data["latency_ms"] >= 0


@patch("requests.request")
def test_test_service_timeout(mock_request):
    mock_request.side_effect = requests.exceptions.Timeout()

    client = app.test_client()
    response = client.post("/api/test-service", json={
        "url": "https://slow-api.example.com",
        "method": "GET"
    })

    assert response.status_code == 504
    data = response.get_json()
    assert data["success"] is False
    assert data["passed"] is False
    assert "timed out" in data["error"].lower()
