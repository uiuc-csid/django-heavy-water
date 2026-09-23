import pytest
from django.test import override_settings

from heavy_water.conf import app_settings


def test_falls_back_to_defaults() -> None:
    assert app_settings.SUPERUSER_USERNAME == "root"
    assert app_settings.FIXTURE_MODULE == ["fixtures"]


def test_reads_overrides_on_each_access() -> None:
    with override_settings(HEAVY_WATER_SUPERUSER_USERNAME="admin"):
        assert app_settings.SUPERUSER_USERNAME == "admin"
    assert app_settings.SUPERUSER_USERNAME == "root"


def test_mutating_a_default_does_not_leak() -> None:
    app_settings.FIXTURE_MODULE.append("other")

    assert app_settings.FIXTURE_MODULE == ["fixtures"]


def test_unknown_setting_raises_attribute_error() -> None:
    with pytest.raises(AttributeError):
        app_settings.NOT_A_SETTING
