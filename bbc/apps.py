from django.apps import AppConfig


class BbcConfig(AppConfig):
    name = 'bbc'

    def ready(self):
        import bbc.signals
