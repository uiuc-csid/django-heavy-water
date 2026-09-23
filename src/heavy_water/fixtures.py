from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from traceback import format_exception
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser, AbstractUser, UserManager

from django.contrib.auth import get_user_model
from django.core.management.base import OutputWrapper
from django.core.management.color import Style
from django.db import transaction

from heavy_water.conf import app_settings


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

    def _heavy_water(self, *args: Any, **kwargs: Any) -> bool:
        try:
            with transaction.atomic():
                self.handle()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully set up data for {self.app_name} - {self.__class__.__name__}"
                    )
                )
            return True
        except AssertionError as ex:
            self.stderr.write(
                self.style.ERROR(
                    f"Assertion failed setting up data for {self.app_name} - {self.__class__.__name__}."
                )
            )
            output = "".join(format_exception(ex))
            self.stderr.write(self.style.ERROR_OUTPUT(output))
            self.stderr.write(self.style.ERROR("Rolling back transaction"))
            return False

    def get_or_create_superuser(
        self,
        username: str | None = None,
        email: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        password: str | None = None,
        configure_user: Callable[[AbstractBaseUser], None] | None = None,
    ) -> AbstractBaseUser:
        # The swappable user model is only typed as AbstractBaseUser, whose manager
        # lacks create_superuser; any model usable with createsuperuser provides it.
        user_manager = cast(
            "UserManager[AbstractUser]", get_user_model()._default_manager
        )

        username = username or app_settings.SUPERUSER_USERNAME
        email = email or app_settings.SUPERUSER_EMAIL
        password = password or app_settings.SUPERUSER_PASSWORD
        first_name = first_name or app_settings.SUPERUSER_FIRST_NAME
        last_name = last_name or app_settings.SUPERUSER_LAST_NAME

        superuser = user_manager.filter(username=username).first()
        if superuser is None:
            superuser = user_manager.create_superuser(
                username=username,
                email=email,
                password=password,
            )

        if configure_user is not None:
            configure_user(superuser)

        superuser.save()
        return superuser

    @abstractmethod
    def handle(self) -> None:
        pass
