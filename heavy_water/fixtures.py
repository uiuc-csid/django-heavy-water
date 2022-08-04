from django.contrib.auth import get_user_model
from django.conf import settings

from heavy_water import BaseDataBuilder


class DataBuilder(BaseDataBuilder):
    def handle(self):
        if settings.HEAVY_WATER_CREATE_ROOT_USER:
            USER_MODEL = get_user_model()

            if not USER_MODEL.objects.filter(
                username=settings.HEAVY_WATER_ROOT_USERNAME
            ):
                USER_MODEL.objects.create_superuser(
                    username=settings.HEAVY_WATER_ROOT_USERNAME,
                    email=settings.HEAVY_WATER_ROOT_EMAIL,
                    password=settings.HEAVY_WATER_ROOT_PASSWORD,
                )

            assert USER_MODEL.objects.filter(
                username=settings.HEAVY_WATER_ROOT_USERNAME,
                email=settings.HEAVY_WATER_ROOT_EMAIL,
            ).exists()
