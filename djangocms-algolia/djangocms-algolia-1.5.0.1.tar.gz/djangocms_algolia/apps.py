from django.apps import AppConfig

from djangocms_algolia.utils.proxy_checker import is_proxy_model_creation_possible


class SearchAppConfig(AppConfig):
    name = 'djangocms_algolia'

    def ready(self) -> None:
        if is_proxy_model_creation_possible():
            # noinspection PyUnresolvedReferences
            from .signals import update_page_index
