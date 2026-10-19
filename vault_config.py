import json
import os
from pathlib import Path

VAULT_CONFIG_FILE = Path(
    os.getenv("VAULT_CONFIG_FILE", "/vault/secrets/config.json")
)

def get_application_config():
    if VAULT_CONFIG_FILE.is_file():
        with VAULT_CONFIG_FILE.open() as f:
            return json.load(f)

    return {
        "APP_ENV": os.getenv("APP_ENV", "development")
    }