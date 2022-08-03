from importlib import import_module

from django.db import transaction
from django.core.management.commands.flush import Command as FlushCommand
from django.utils.module_loading import module_has_submodule
from django.conf import settings
from django.contrib.auth import get_user_model
from django.apps import apps


class Command(FlushCommand):
    help = "Creates a superuser and generates test data"
    requires_migrations_checks = True

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--wipe', action='store_true',
            help='Wipe the database?',
        )
    
    @transaction.atomic
    def handle(self, *args, **options):
        if options.get('wipe'):
            super().handle(*args, **options)

        USER_MODEL = get_user_model()

        if not USER_MODEL.objects.filter(username=settings.DEV_DATA_ROOT_USERNAME):
            USER_MODEL.objects.create_superuser(username=settings.DEV_DATA_ROOT_USERNAME, email=settings.DEV_DATA_ROOT_EMAIL, password=settings.DEV_DATA_ROOT_PASSWORD)
        
        for app in apps.get_app_configs():
            if module_has_submodule(app.module, 'management.setup_dev_data'):
                # TOOD: execute each of these in an independent transaction so they can be rolled back if needed
                try:
                    import_module(f"{app.name}.management.setup_dev_data")
                    self.stdout.write(self.style.SUCCESS(f"Dev data for {app.name} successfully setup"))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error setting up dev data for {app.name}: {e}"))
