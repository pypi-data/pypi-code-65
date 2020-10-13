from datetime import datetime
from typing import List
from typing import Union

from aldryn_search.search_indexes import TitleIndex
from algoliasearch_django import AlgoliaIndex
from algoliasearch_django import register
from cms.models import Title
from cms.test_utils.testcases import BaseCMSTestCase
from cms.toolbar.toolbar import CMSToolbar
from django.conf import settings
from django.db.models import QuerySet
from django.forms import Media
from django.http import HttpRequest
from django.test import Client
from haystack.indexes import SearchIndex

from djangocms_algolia.utils.proxy_checker import is_proxy_model_creation_possible


class FakeCMSRequestFactor(BaseCMSTestCase):
    client = Client

    def get_request(self, *args, **kwargs) -> HttpRequest:
        request = super().get_request(*args, **kwargs)
        request.placeholder_media = Media()
        request.session = {}
        request.toolbar = CMSToolbar(request)
        return request


if is_proxy_model_creation_possible():

    class TitleProxy(Title):
        model_type = 'page'

        def search_index_description(self) -> str:
            aldryn_haystack_index: Union[SearchIndex, TitleIndex] = TitleIndex()
            page_content: str = aldryn_haystack_index.get_search_data(
                obj=self,
                language=self.language,
                request=FakeCMSRequestFactor().get_request(),
            )
            if settings.ALGOLIA_SEARCH_INDEX_TEXT_LIMIT:
                return page_content[:settings.ALGOLIA_SEARCH_INDEX_TEXT_LIMIT]
            else:
                return page_content

        def pub_date(self) -> datetime:
            return self.page.publication_date

        def url(self) -> str:
            return self.page.get_absolute_url(language=self.language)

        class Meta:
            app_label = 'cms'
            proxy = True


    class PageIndex(AlgoliaIndex):
        language = 'en'
        should_index = 'published'

        fields = [
            'title',
            'url',
            'pub_date',
            'meta_description',
            'search_index_description',
        ]

        def get_queryset(self) -> QuerySet:
            aldryn_haystack_index: SearchIndex = TitleIndex()
            return aldryn_haystack_index.get_index_queryset(
                language=self.language,
            )

    page_indices: List = []

    for language in settings.LANGUAGES:
        if (
            getattr(settings, 'ALGOLIA_IS_ENABLE_ENV_SPECIFIC_INDEXES', False) and
            hasattr(settings, 'DJANGO_ENV')
        ):
            index_name = f'{settings.DJANGO_ENV.value}_cms_pages_{language[0]}'
        else:
            index_name = f'cms_pages_{language[0]}'

        index_cls_init_args = {
            'language': language[0],
            'index_name': index_name,
            '__module__': __name__
        }
        index_cls_bases = (PageIndex,)
        index_cls = type(f'PageIndex{language[0]}', index_cls_bases, index_cls_init_args)
        page_indices.append(index_cls)


    class MultiLangAlgoliaIndex(AlgoliaIndex):
        # noinspection PyMissingConstructor
        def __init__(self, model, client, settings):
            self.indices = []

            for index_cls in page_indices:
                self.indices.append(index_cls(model, client, settings))

        def raw_search(self, query='', params=None):
            res = {}
            for index in self.indices:
                res[index.name] = index.raw_search(query, params)
            return res

        def update_records(self, qs, batch_size=1000, **kwargs):
            for index in self.indices:
                index.update_records(qs, batch_size, **kwargs)

        def reindex_all(self, batch_size=1000):
            for index in self.indices:
                index.reindex_all(batch_size)

        def set_settings(self):
            for index in self.indices:
                index.set_settings()

        def clear_index(self):
            for index in self.indices:
                index.clear_index()

        def save_record(self, instance, update_fields=None, **kwargs):
            for index in self.indices:
                index.save_record(instance, update_fields, **kwargs)

        def delete_record(self, instance):
            for index in self.indices:
                index.delete_record(instance)


    register(TitleProxy, MultiLangAlgoliaIndex)
