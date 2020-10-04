from typing import List

from aldryn_search.helpers import get_plugin_index_data
from aldryn_search.utils import clean_join
from cms.models import CMSPlugin
from cms.models import Placeholder
from django.conf import settings
from django.http import HttpRequest

from djangocms_algolia.index import FakeCMSRequestFactor


def render_text_from_placeholders(placeholders: List[Placeholder], lang_code: str = settings.LANGUAGE_CODE) -> str:
    indexable_strings: List[str] = []
    for placeholder in placeholders:
        indexable_strings.append(render_text_from_placeholder(placeholder, lang_code))
    return clean_join(' ', indexable_strings)


def render_text_from_placeholder(placeholder: Placeholder, lang_code: str = settings.LANGUAGE_CODE) -> str:
    indexable_strings: List[str] = []
    plugins = CMSPlugin.objects.filter(language=lang_code).filter(placeholder=placeholder)
    for plugin in plugins:
        request_fake = FakeCMSRequestFactor().get_request()
        plugin_text_content = render_text_from_plugin(plugin, request_fake)
        indexable_strings.append(plugin_text_content)
    return clean_join(' ', indexable_strings)


def render_text_from_plugin(plugin: CMSPlugin, request: HttpRequest) -> str:
    return clean_join(' ', get_plugin_index_data(plugin, request))
