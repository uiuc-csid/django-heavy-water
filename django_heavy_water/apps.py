from django.apps import AppConfig


class HeavyWaterConfig(AppConfig):
    name = 'heavy_water'
    SETTINGS_MODULE = 'app_settings'

    def ready(self):
        from django.conf import settings
        from . import app_settings as defaults

        for name in dir(defaults):
            if name.isupper() and not hasattr(settings, name):
                setattr(settings, name, getattr(defaults, name))
