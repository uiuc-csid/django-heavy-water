from importlib import import_module
from inspect import getmembers, isclass
from traceback import print_exc

from django.apps import apps
from django.conf import settings
from django.core.management.commands.flush import Command as FlushCommand
from django.db import transaction
from django.utils.module_loading import module_has_submodule

from heavy_water import BaseDataBuilder


class Command(FlushCommand):
    help = "Creates a superuser and generates test data"
    requires_migrations_checks = True

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--wipe",
            action="store_true",
            help="Wipe the database?",
        )

        # TODO(joshuata): Add arguments for tagged data fixtures

    @transaction.atomic
    def handle(self, *args, **options):
        if options.get("wipe"):
            super().handle(*args, **options)

        data_builders = []
        for app in apps.get_app_configs():
            for module_name in settings.HEAVY_WATER_FIXTURE_MODULE:
                if not module_has_submodule(app.module, module_name):
                    continue
                module = import_module(f"{app.name}.{module_name}")
                for name, member in getmembers(module):
                    if (
                        isclass(member)
                        and issubclass(member, BaseDataBuilder)
                        and not member == BaseDataBuilder
                    ):
                        setattr(member, "app_name", app.name)
                        data_builders.append(member)

        for builder in data_builders:
            try:
                obj = builder(
                    app_name=builder.app_name,
                    stdout=self.stdout,
                    stderr=self.stderr,
                    style=self.style,
                )
                obj._heavy_water()
            except Exception:
                print_exc()  # TODO(joshuata): print to self.stderr
