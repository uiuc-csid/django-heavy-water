from django.conf import settings

CREATE_ROOT_USER: bool = getattr(settings, "HEAVY_WATER_CREATE_ROOT_USER", True)
SUPERUSER_USERNAME: str = getattr(settings, "HEAVY_WATER_SUPERUSER_USERNAME", "root")
SUPERUSER_EMAIL: str = getattr(
    settings, "HEAVY_WATER_SUPERUSER_EMAIL", "root@example.com"
)
SUPERUSER_PASSWORD: str = getattr(
    settings, "HEAVY_WATER_SUPERUSER_PASSWORD", "rootroot"
)  # noqa: S105
SUPERUSER_FIRST_NAME: str = getattr(
    settings, "HEAVY_WATER_SUPERUSER_FIRST_NAME", "Root"
)
SUPERUSER_LAST_NAME: str = getattr(settings, "HEAVY_WATER_SUPERUSER_LAST_NAME", "User")
FIXTURE_MODULE: list[str] = getattr(
    settings, "HEAVY_WATER_FIXTURE_MODULE", ["fixtures"]
)

ENV_MAPPING: dict[str, list[str]] = getattr(
    settings,
    "HEAVY_WATER_ENV_MAPPING",
    {
        "development": ["DEV"],
        "test": ["TEST"],
        "staging": ["STAGING"],
        "production": ["PROD"],
    },
)
