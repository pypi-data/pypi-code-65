from unittest import mock

import pytest

from scarlet.cache.router import router
from .cache_groups import CACHE_KEY
from .views import DummyCacheView

CACHE = router.get_cache()


@pytest.mark.urls("cache_views.urls")
class TestViews:
    def teardown_method(self):
        CACHE.clear()

    def test_basic_get(self, client):
        client.get("/dummy_cache_view/")
        assert CACHE.get(CACHE_KEY) == 0

    def test_get_cache_version_not_implemented(self, client):
        client.get("/get_cache_version_not_implemented_view")
        assert CACHE.get(CACHE_KEY) is None

    def test_staff_user_should_not_cache(self, rf):
        request = rf.get("/dummy_cache_view/")
        request.user = mock.Mock()
        request.user.is_staff = True

        DummyCacheView.as_view()(request)
        assert CACHE.get(CACHE_KEY) is None
