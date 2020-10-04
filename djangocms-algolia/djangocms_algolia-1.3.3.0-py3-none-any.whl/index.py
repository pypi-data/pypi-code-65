import re
from datetime import datetime
from typing import Union

from aldryn_search.search_indexes import TitleIndex
from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register
from cms.models import Title
from cms.test_utils.testcases import BaseCMSTestCase
from cms.toolbar.toolbar import CMSToolbar
from django.conf import settings
from django.db import connection
from django.db.models import QuerySet
from django.forms import Media
from django.http import HttpRequest
from django.test import Client
from django.utils import translation
from haystack.indexes import SearchIndex


def _is_proxy_model_creation_possible() -> bool:
    """
    A proxy model cannot be imported in django when the parent table doesn't exists.
    But algolia django package tries to import the models before the user runs `python manage.py migrate`,
    which throws a django exception.
    
    In other words algoliasearch-django package prevents you from creating a database in the first place.
    """
    return 'cms_title' in connection.introspection.table_names()


class FakeCMSRequestFactor(BaseCMSTestCase):
    client = Client
    
    def get_request(self, *args, **kwargs) -> HttpRequest:
        request = super().get_request(*args, **kwargs)
        request.placeholder_media = Media()
        request.session = {}
        request.toolbar = CMSToolbar(request)
        return request


if _is_proxy_model_creation_possible():

    class AlgoliaPageDataProxy(Title):
        model_type = 'page'

        def search_index_description(self) -> str:
            aldryn_haystack_index: Union[SearchIndex, TitleIndex] = TitleIndex()
            page_content: str = aldryn_haystack_index.get_search_data(
                obj=self,
                language=translation.get_language(),
                request=FakeCMSRequestFactor().get_request(),
            )
            if settings.ALGOLIA_SEARCH_INDEX_TEXT_LIMIT:
                return page_content[:settings.ALGOLIA_SEARCH_INDEX_TEXT_LIMIT]
            else:
                return page_content

        def pub_date(self) -> datetime:
            return self.page.publication_date

        def url(self) -> str:
            lang_prefix = f'/{translation.get_language()}/'
            url_with_lang = self.page.get_absolute_url()
            url_without_lang = re.sub(rf'^{lang_prefix}', '', url_with_lang)
            return url_without_lang

        class Meta:
            app_label = 'cms'
            proxy = True


    @register(AlgoliaPageDataProxy)
    class PageIndex(AlgoliaIndex):
        if hasattr(settings, 'DJANGO_ENV'):
            index_name =  f'{settings.DJANGO_ENV.value}_cms_pages'
        else:
            index_name =  'cms_pages'

        fields = [
            'title',
            'url',
            'pub_date',
            'meta_description',
            'search_index_description',
        ]

        # def __init__(self, model, client, settings):
        #     lang_code_current: str = translation.get_language()
        #     settings_with_postfix = settings or {}
        #     settings_with_postfix['INDEX_SUFFIX'] = lang_code_current
        #     super().__init__(model, client, settings)

        def get_queryset(self) -> QuerySet:
            aldryn_haystack_index: SearchIndex = TitleIndex()
            return aldryn_haystack_index.get_index_queryset(
                language=translation.get_language(),
            )
