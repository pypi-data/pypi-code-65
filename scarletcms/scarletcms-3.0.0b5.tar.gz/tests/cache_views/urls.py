from django.urls import path

from .views import DummyCacheView, GetCacheVersionNotImplementedView

urlpatterns = [
    path("dummy_cache_view/", DummyCacheView.as_view(),),
    path("get_cache_version_not_implemented_view/", GetCacheVersionNotImplementedView.as_view(),),
]
