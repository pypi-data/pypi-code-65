from typing import List

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from cms.models import Page


@apphook_pool.register
class DjangocmsAlgoliaApphook(CMSApp):
    app_name = 'djangocms_algolia'
    name = "Search"

    def get_urls(self, page: Page = None, language: str = None, **kwargs) -> List[str]:
        return [f'{self.app_name}.urls']
