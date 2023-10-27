from importlib import import_module
from inspect import getmembers, isclass
from traceback import print_exception

from django.apps import apps
from django.conf import settings
from django.core.management.commands.flush import Command as FlushCommand
from django.db import transaction
from django.utils.module_loading import module_has_submodule

from heavy_water import BaseDataBuilder
from heavy_water.settings import ENV_MAPPING, FIXTURE_MODULE


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

    @transaction.atomic
    def handle(self, *args, **options):
        if options.get("wipe"):
            super().handle(*args, **options)

        data_builders = []
        for app in apps.get_app_configs():
            for module_name in FIXTURE_MODULE:
                if not module_has_submodule(app.module, module_name):
                    continue
                module = import_module(f"{app.name}.{module_name}")
                for _, member in getmembers(module):
                    if (
                        isclass(member)
                        and issubclass(member, BaseDataBuilder)
                        and not member == BaseDataBuilder
                    ):
                        setattr(member, "app_name", app.name)
                        data_builders.append(member)

        tag_list = ENV_MAPPING.get(settings.DJANGO_ENV, None)
        for builder in data_builders:
            # Check whether the builder should execute given the current env
            if any([getattr(builder, tag, False) for tag in tag_list]):
                try:
                    obj = builder(
                        app_name=builder.app_name,
                        stdout=self.stdout,
                        stderr=self.stderr,
                        style=self.style,
                    )
                    obj._heavy_water()
                except Exception as ex:
                    print_exception(value=ex, file=self.stderr)
