from io import StringIO
from typing import Any

import pytest
from django.core.management import CommandError, call_command
from django.test import override_settings

from heavy_water.management.commands.heavy_water import Command
from tests.testapp import fixtures, fixtures_mixed, fixtures_options
from tests.testapp.models import Record

pytestmark = pytest.mark.django_db


def run(**options: object) -> tuple[str, str]:
    stdout, stderr = StringIO(), StringIO()
    call_command("heavy_water", stdout=stdout, stderr=stderr, **options)
    return stdout.getvalue(), stderr.getvalue()


def record_names() -> set[str]:
    return set(Record.objects.values_list("name", flat=True))


class TestDiscovery:
    def test_finds_builders_in_default_module(self) -> None:
        assert Command()._discover_builders() == [("tests.testapp", fixtures.Basic)]

    @override_settings(HEAVY_WATER_FIXTURE_MODULE=["fixtures", "fixtures_options"])
    def test_searches_every_configured_module(self) -> None:
        assert Command()._discover_builders() == [
            ("tests.testapp", fixtures.Basic),
            ("tests.testapp", fixtures_options.WipeOnly),
        ]

    @override_settings(HEAVY_WATER_FIXTURE_MODULE=["does_not_exist"])
    def test_skips_apps_without_the_module(self) -> None:
        assert Command()._discover_builders() == []

    @override_settings(HEAVY_WATER_FIXTURE_MODULE=["fixtures_mixed"])
    def test_ignores_the_base_class(self) -> None:
        builders = [builder for _, builder in Command()._discover_builders()]
        assert builders == [
            fixtures_mixed.FailsAssertion,
            fixtures_mixed.Raises,
            fixtures_mixed.Skipped,
            fixtures_mixed.Succeeds,
        ]


class TestRun:
    def test_runs_builders_and_reports_success(self) -> None:
        stdout, stderr = run()

        assert record_names() == {"basic"}
        assert "tests.testapp - Basic: Successfully set up data" in stdout
        assert stderr == ""

    @override_settings(HEAVY_WATER_FIXTURE_MODULE=["fixtures_mixed"])
    def test_failures_roll_back_only_the_failing_builder(self) -> None:
        with pytest.raises(CommandError) as excinfo:
            run()

        assert record_names() == {"succeeds"}
        assert str(excinfo.value) == (
            "2 data builder(s) failed: "
            "tests.testapp - FailsAssertion, tests.testapp - Raises"
        )

    @override_settings(HEAVY_WATER_FIXTURE_MODULE=["fixtures", "fixtures_init"])
    def test_failure_creating_a_builder_is_reported_by_class_name(self) -> None:
        with pytest.raises(CommandError) as excinfo:
            run()

        assert record_names() == {"basic"}
        assert str(excinfo.value) == (
            "1 data builder(s) failed: tests.testapp - BrokenInit"
        )

    @override_settings(HEAVY_WATER_FIXTURE_MODULE=["fixtures_mixed"])
    def test_failures_are_reported_to_stderr(self) -> None:
        stderr = StringIO()
        with pytest.raises(CommandError):
            call_command("heavy_water", stdout=StringIO(), stderr=stderr)

        output = stderr.getvalue()
        assert (
            "tests.testapp - FailsAssertion: Assertion failed setting up data" in output
        )
        assert "deliberate assertion failure" in output
        assert "RuntimeError: deliberate error" in output

    @override_settings(HEAVY_WATER_FIXTURE_MODULE=["fixtures_mixed"])
    def test_skips_builders_whose_should_run_is_false(self) -> None:
        stdout = StringIO()
        with pytest.raises(CommandError):
            call_command("heavy_water", stdout=stdout, stderr=StringIO())

        assert "skipped" not in record_names()
        assert "tests.testapp - Skipped: Skipped" in stdout.getvalue()


class TestOptions:
    @pytest.fixture(autouse=True)
    def fixture_modules(self, settings: Any) -> None:
        settings.HEAVY_WATER_FIXTURE_MODULE = ["fixtures", "fixtures_options"]

    def test_should_run_receives_command_options(self) -> None:
        run(verbosity=2)

        assert fixtures_options.WipeOnly.received_options["verbosity"] == 2
        assert fixtures_options.WipeOnly.received_options["wipe"] is False
        assert record_names() == {"basic"}

    def test_wipe_flushes_before_building(self) -> None:
        Record.objects.create(name="stale")

        run(wipe=True, interactive=False)

        assert record_names() == {"basic", "wipe-only"}
        assert fixtures_options.WipeOnly.received_options["wipe"] is True
