from copy import deepcopy
from typing import Any

from django.conf import settings

DEFAULTS: dict[str, Any] = {
    "SUPERUSER_USERNAME": "root",
    "SUPERUSER_EMAIL": "root@example.com",
    "SUPERUSER_PASSWORD": "rootroot",
    "SUPERUSER_FIRST_NAME": "Root",
    "SUPERUSER_LAST_NAME": "User",
    "FIXTURE_MODULE": ["fixtures"],
    "ENV_MAPPING": {
        "development": ["DEV"],
        "test": ["TEST"],
        "staging": ["STAGING"],
        "production": ["PROD"],
    },
}


class HeavyWaterSettings:
    """Reads ``HEAVY_WATER_<NAME>`` from Django settings on every access, so
    ``override_settings`` takes effect."""

    SUPERUSER_USERNAME: str
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str
    SUPERUSER_FIRST_NAME: str
    SUPERUSER_LAST_NAME: str
    FIXTURE_MODULE: list[str]
    ENV_MAPPING: dict[str, list[str]]

    def __getattr__(self, name: str) -> Any:
        if name not in DEFAULTS:
            raise AttributeError(name)
        return getattr(settings, f"HEAVY_WATER_{name}", deepcopy(DEFAULTS[name]))


app_settings = HeavyWaterSettings()
