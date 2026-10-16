
from app import app


def test_home():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert response.json["application"] == "gitops-advanced-app"


def test_liveness():
    client = app.test_client()
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json["status"] == "alive"


def test_readiness():
    client = app.test_client()
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json["status"] == "ready"


def test_info():
    client = app.test_client()
    response = client.get("/api/info")

    assert response.status_code == 200
    assert "hostname" in response.json

def test_cpu_load():
    client = app.test_client()
    response = client.get("/api/load")

    assert response.status_code == 200
    assert response.json["status"] == "completed"
