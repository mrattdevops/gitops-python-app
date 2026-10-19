import json
from pathlib import Path

import pytest

import application_config


@pytest.fixture
def config_file(tmp_path, monkeypatch):
    path = tmp_path / "config"
    monkeypatch.setattr(application_config, "CONFIG_FILE", path)
    return path


def test_config_path_is_fixed():
    assert application_config.CONFIG_FILE == Path("/vault/secrets/config")


def test_read_config(config_file):
    config_file.write_text('{"APP_ENV":"development"}', encoding="utf-8")

    assert application_config.get_application_config() == {"APP_ENV": "development"}


def test_config_refresh(config_file):
    config_file.write_text('{"APP_ENV":"development"}', encoding="utf-8")
    first = application_config.get_application_config()
    config_file.write_text('{"APP_ENV":"updated"}', encoding="utf-8")
    second = application_config.get_application_config()

    assert first["APP_ENV"] == "development"
    assert second["APP_ENV"] == "updated"


def test_missing_file_uses_environment(config_file, monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    assert application_config.get_application_config() == {"APP_ENV": "local"}


def test_missing_file_uses_existing_default(config_file, monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    assert application_config.get_application_config() == {"APP_ENV": "development"}


def test_no_secret_keys_are_required(config_file):
    config_file.write_text("{}", encoding="utf-8")
    assert application_config.get_application_config() == {}


@pytest.mark.parametrize("contents", ["", "invalid", "[]", "null", "42", '"text"'])
def test_invalid_config_is_rejected_without_contents(config_file, contents):
    config_file.write_text(contents, encoding="utf-8")
    with pytest.raises(application_config.ConfigurationError) as error:
        application_config.get_application_config()
    assert str(error.value) in (
        "Application configuration is unavailable.",
        "Application configuration must be a JSON object.",
    )


@pytest.mark.parametrize("value", [None, 42, True, [], {}, "", "  "])
def test_invalid_app_env_is_rejected(config_file, value):
    config_file.write_text(json.dumps({"APP_ENV": value}), encoding="utf-8")
    with pytest.raises(application_config.ConfigurationError, match="APP_ENV must"):
        application_config.get_application_config()


def test_invalid_encoding_is_rejected(config_file):
    config_file.write_bytes(b"\xff")
    with pytest.raises(application_config.ConfigurationError):
        application_config.get_application_config()


def test_unreadable_file_is_rejected(config_file, monkeypatch):
    def denied(*args, **kwargs):
        raise PermissionError("Access denied")

    monkeypatch.setattr(Path, "open", denied)
    with pytest.raises(application_config.ConfigurationError):
        application_config.get_application_config()


def test_directory_is_rejected(config_file):
    config_file.mkdir()
    with pytest.raises(application_config.ConfigurationError):
        application_config.get_application_config()
