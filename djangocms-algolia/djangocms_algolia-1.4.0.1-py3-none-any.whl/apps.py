from django.apps import AppConfig


class SearchAppConfig(AppConfig):
    name = 'djangocms_algolia'

    def ready(self) -> None:
        from .signals import update_page_index