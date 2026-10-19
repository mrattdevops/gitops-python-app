
import json

import vault_config


def test_read_vault_config(tmp_path, monkeypatch):
    config_file = tmp_path / "config.json"
    config_file.write_text(
        json.dumps({
            "APP_ENV": "development",
            "DEMO_API_KEY": "test-value"
        })
    )

    monkeypatch.setattr(
        vault_config,
        "VAULT_CONFIG_FILE",
        config_file
    )

    config = vault_config.get_application_config()

    assert config["APP_ENV"] == "development"
    assert config["DEMO_API_KEY"] == "test-value"


def test_config_refresh(tmp_path, monkeypatch):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"APP_ENV":"development"}')

    monkeypatch.setattr(
        vault_config,
        "VAULT_CONFIG_FILE",
        config_file
    )

    first = vault_config.get_application_config()

    config_file.write_text('{"APP_ENV":"updated"}')

    second = vault_config.get_application_config()

    assert first["APP_ENV"] == "development"
    assert second["APP_ENV"] == "updated"


def test_fallback_when_vault_file_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(
        vault_config,
        "VAULT_CONFIG_FILE",
        tmp_path / "missing.json"
    )
    monkeypatch.setenv("APP_ENV", "local")

    config = vault_config.get_application_config()

    assert config["APP_ENV"] == "local"
