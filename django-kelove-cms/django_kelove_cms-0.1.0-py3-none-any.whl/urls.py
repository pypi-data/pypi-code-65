# ==================================================================
#       文 件 名: urls.py
#       概    要: 路由配置
#       作    者: IT小强 
#       创建时间: 8/12/20 4:16 PM
#       修改时间: 
#       copyright (c) 2016 - 2020 mail@xqitw.cn
# ==================================================================

from django.conf.urls import url
from django.urls import path

from . import views
from .apps import DjangoKeloveCmsConfig
from .settings import GlobalSettingsForm

__all__ = ['urlpatterns', 'app_name']

app_name = DjangoKeloveCmsConfig.name

global_settings = GlobalSettingsForm.get()

default_tag_url = r'^tag/(?P<pk>[\w-]+)/page/(?P<page>[\w-]+)/$'
default_tag_home_url = r'^tag/(?P<pk>[\w-]+)/$'

default_category_url = r'^category/(?P<pk>[\w-]+)/page/(?P<page>[\w-]+)/$'
default_category_home_url = r'^category/(?P<pk>[\w-]+)/$'

default_document_url = r'^(?P<pk>[\w-]+)/page/(?P<page>[\w-]+)/$'
default_document_home_url = r'^(?P<pk>[\w-]+).html$'

default_search_url = r'^search/page/(?P<page>[\w-]+)/$'
default_search_home_url = r'^search/$'
tag_url = global_settings.get('tag_url', default_tag_url)
tag_home_url = global_settings.get('tag_home_url', default_tag_home_url)

category_url = global_settings.get('category_url', default_category_url)
category_home_url = global_settings.get('category_home_url', default_category_home_url)

document_url = global_settings.get('document_url', default_document_url)
document_home_url = global_settings.get('document_home_url', default_document_home_url)

search_url = global_settings.get('search_url', default_search_url)
search_home_url = global_settings.get('search_home_url', default_search_home_url)

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    url(
        search_url if search_url else default_search_url,
        views.Search.as_view(),
        name='search'
    ),
    url(
        search_home_url if search_home_url else default_search_home_url,
        views.Search.as_view(),
        name='search_home'
    ),
    url(
        tag_home_url if tag_home_url else default_tag_home_url,
        views.Tag.as_view(),
        name='tag_home'
    ),
    url(
        tag_url if tag_url else default_tag_url,
        views.Tag.as_view(),
        name='tag'
    ),
    url(
        category_home_url if category_home_url else default_category_home_url,
        views.Category.as_view(),
        name='category_home'
    ),
    url(
        category_url if category_url else default_category_url,
        views.Category.as_view(),
        name='category'
    ),
    url(
        document_home_url if document_home_url else default_document_home_url,
        views.Document.as_view(),
        name='document_home'
    ),
    url(
        document_url if document_url else default_document_url,
        views.Document.as_view(),
        name='document'
    ),
]
