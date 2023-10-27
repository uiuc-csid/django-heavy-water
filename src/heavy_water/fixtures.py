from __future__ import annotations

from abc import ABC, abstractmethod
from traceback import format_exception
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser

from django.contrib.auth import get_user_model
from django.core.management.base import OutputWrapper
from django.core.management.color import Style
from django.db import transaction

from heavy_water import settings


class BaseDataBuilder(ABC):
    DEV = True
    TEST = False
    STAGING = False
    PROD = False

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
                    self.style.SUCCESS(
                        f"Successfully set up data for {self.app_name} - {self.__class__.__name__}"
                    )
                )
        except AssertionError as ex:
            self.stderr.write(
                self.style.ERROR(
                    f"Assertion failed setting up data for {self.app_name} - {self.__class__.__name__}."
                )
            )
            output = format_exception(ex)
            output = "\n".join(output)
            self.stderr.write(self.style.ERROR_OUTPUT(output))
            self.stderr.write(self.style.ERROR("Rolling back transaction"))

    def get_or_create_superuser(
        self,
        username=None,
        email=None,
        first_name=None,
        last_name=None,
        password=None,
        configure_user: Optional[Callable[[AbstractBaseUser], None]] = None,
    ):
        USER_MODEL = get_user_model()

        username = username or settings.SUPERUSER_USERNAME
        email = email or settings.SUPERUSER_EMAIL
        password = password or settings.SUPERUSER_PASSWORD
        first_name = first_name or settings.SUPERUSER_FIRST_NAME
        last_name = last_name or settings.SUPERUSER_LAST_NAME

        superuser = list(
            USER_MODEL.objects.filter(
                username=username,
            )
        )
        if not superuser:
            superuser = USER_MODEL.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
        else:
            superuser = superuser[0]

        if configure_user is not None:
            configure_user(superuser)

        superuser.save()
        return superuser

    @abstractmethod
    def handle(self):
        pass
