from django.conf import settings

from heavy_water import BaseDataBuilder


class DataBuilder(BaseDataBuilder):
    def handle(self):
        if settings.HEAVY_WATER_CREATE_ROOT_USER:
            self.get_or_create_superuser()
