from django.conf.urls import url

from djangocms_algolia.views import AlgoliaSearchView


urlpatterns = [
    url('^$', AlgoliaSearchView.as_view(), name='algolia-search'),
]
