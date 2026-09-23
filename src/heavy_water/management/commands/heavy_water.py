from importlib import import_module
from inspect import getmembers, isclass
from traceback import format_exception
from typing import Any

from django.apps import apps
from django.conf import settings
from django.core.management.base import CommandError, CommandParser
from django.core.management.commands.flush import Command as FlushCommand
from django.db import transaction
from django.utils.module_loading import module_has_submodule

from heavy_water import BaseDataBuilder
from heavy_water.conf import app_settings


class Command(FlushCommand):
    help = "Runs the data builders for the current environment"
    requires_migrations_checks = True

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--wipe",
            action="store_true",
            help="Wipe the database?",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        # Commit whatever succeeded before reporting failure, so a single bad
        # builder doesn't roll back the others.
        with transaction.atomic():
            failures = self._build(*args, **options)
        if failures:
            raise CommandError(
                f"{len(failures)} data builder(s) failed: {', '.join(failures)}"
            )

    def _build(self, *args: Any, **options: Any) -> list[str]:
        if options.get("wipe"):
            super().handle(*args, **options)

        failures: list[str] = []
        env = getattr(settings, "DJANGO_ENV", None)
        env_mapping = app_settings.ENV_MAPPING
        tag_list = env_mapping.get(env) if env is not None else None
        if tag_list is None:
            raise CommandError(
                f"settings.DJANGO_ENV must be one of {sorted(env_mapping)}, got {env!r}"
            )
        for app_name, builder in self._discover_builders():
            # Check whether the builder should execute given the current env
            if any([getattr(builder, tag, False) for tag in tag_list]):
                try:
                    obj = builder(
                        app_name=app_name,
                        stdout=self.stdout,
                        stderr=self.stderr,
                        style=self.style,
                    )
                    succeeded = obj._heavy_water()
                except Exception as ex:
                    succeeded = False
                    output = "".join(format_exception(ex))
                    self.stderr.write(self.style.ERROR_OUTPUT(output))
                if not succeeded:
                    failures.append(f"{app_name}.{builder.__name__}")
        return failures

    def _discover_builders(self) -> list[tuple[str, type[BaseDataBuilder]]]:
        data_builders: list[tuple[str, type[BaseDataBuilder]]] = []
        for app in apps.get_app_configs():
            for module_name in app_settings.FIXTURE_MODULE:
                if not module_has_submodule(app.module, module_name):
                    continue
                module = import_module(f"{app.name}.{module_name}")
                for _, member in getmembers(module):
                    if (
                        isclass(member)
                        and issubclass(member, BaseDataBuilder)
                        and not member == BaseDataBuilder
                    ):
                        data_builders.append((app.name, member))

        return data_builders
