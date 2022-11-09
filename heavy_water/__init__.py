from abc import ABC, abstractmethod
from traceback import print_exc
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import OutputWrapper
from django.core.management.color import Style
from django.db import transaction


class BaseDataBuilder(ABC):
    def __init__(
        self, app_name: str, stdout: OutputWrapper, stderr: OutputWrapper, style: Style
    ) -> None:
        self.app_name = app_name
        self.stdout = stdout
        self.stderr = stderr
        self.style = style

    def _heavy_water(self, *args: Any, **kwargs: Any) -> Any:
        try:
            with transaction.atomic():
                self.handle()
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully set up data for {self.app_name}")
                )
        except AssertionError:
            self.stderr.write(
                self.style.ERROR(
                    f"Assertion failed setting up data for {self.app_name}."
                )
            )
            print_exc()  # TODO: print to self.stderr
            self.stderr.write(self.style.ERROR("Rolling back transaction"))

    def get_or_create_superuser(self, username=None, email=None, password=None):
        USER_MODEL = get_user_model()

        username = username or settings.HEAVY_WATER_ROOT_USERNAME
        email = email or settings.HEAVY_WATER_ROOT_EMAIL
        password = password or settings.HEAVY_WATER_ROOT_PASSWORD

        if not USER_MODEL.objects.filter(
            username=username,
        ):
            USER_MODEL.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )

        superuser = USER_MODEL.objects.get(
            username=username,
        )

        return superuser

    @abstractmethod
    def handle(self):
        pass
