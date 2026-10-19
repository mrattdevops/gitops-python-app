"""Read application configuration from the runtime-mounted JSON file."""

import json
import os
from pathlib import Path

CONFIG_FILE = Path("/vault/secrets/config")


class ConfigurationError(Exception):
    """Configuration cannot be read or does not have the expected format."""


def get_application_config():
    # Read on each call so updates to the mounted file are picked up.
    try:
        with CONFIG_FILE.open(encoding="utf-8") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        # The application currently has no required secrets.
        return {"APP_ENV": os.getenv("APP_ENV", "development")}
    except (OSError, UnicodeError, json.JSONDecodeError):
        # Never include file contents or parser errors in diagnostics.
        raise ConfigurationError("Application configuration is unavailable.") from None

    if not isinstance(config, dict):
        raise ConfigurationError("Application configuration must be a JSON object.")
    if "APP_ENV" in config and (
        not isinstance(config["APP_ENV"], str) or not config["APP_ENV"].strip()
    ):
        raise ConfigurationError("APP_ENV must be a non-empty string.")

    return config
