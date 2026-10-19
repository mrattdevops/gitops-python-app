
import pytest

import application_config
from app import app


@pytest.fixture(autouse=True)
def config_file(tmp_path, monkeypatch):
    path = tmp_path / "config"
    monkeypatch.setattr(application_config, "CONFIG_FILE", path)
    return path


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
    assert response.json["vault_config_loaded"] is False


def test_info_uses_file_environment(config_file, monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    config_file.write_text('{"APP_ENV":"development"}', encoding="utf-8")

    response = app.test_client().get("/api/info")

    assert response.status_code == 200
    assert response.json["environment"] == "development"
    assert response.json["vault_config_loaded"] is True


def test_info_without_app_env_uses_environment(config_file, monkeypatch):
    config_file.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("APP_ENV", "local")

    response = app.test_client().get("/api/info")

    assert response.status_code == 200
    assert response.json["environment"] == "local"


@pytest.mark.parametrize("endpoint", ["/api/info", "/health/ready"])
@pytest.mark.parametrize("contents", ["invalid", "[]", '{"APP_ENV":null}'])
def test_invalid_config_returns_safe_error(config_file, endpoint, contents, caplog):
    config_file.write_text(contents, encoding="utf-8")

    response = app.test_client().get(endpoint)

    assert response.status_code == 503
    assert response.json == {"error": "Application configuration is unavailable."}
    assert not caplog.records


def test_liveness_works_with_invalid_config(config_file):
    config_file.write_text("invalid", encoding="utf-8")
    assert app.test_client().get("/health/live").status_code == 200


def test_readiness_recovers_after_file_update(config_file):
    client = app.test_client()
    config_file.write_text("invalid", encoding="utf-8")
    assert client.get("/health/ready").status_code == 503
    config_file.write_text("{}", encoding="utf-8")
    assert client.get("/health/ready").status_code == 200


def test_cpu_load():
    client = app.test_client()
    response = client.get("/api/load")

    assert response.status_code == 200
    assert response.json["status"] == "completed"

def test_prometheus_metrics():
    client = app.test_client()

    client.get("/api/info")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert b"http_requests_total" in response.data