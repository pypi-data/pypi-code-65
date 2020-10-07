from rest_framework import (
    pagination,
    settings,
)
from .settings import MB_VIEWS

PAGE_SIZE = MB_VIEWS.get(
    'PAGE_SIZE', settings.api_settings.PAGE_SIZE)
PAGE_SIZE_MAX = MB_VIEWS.get(
    'PAGE_SIZE_MAX', 1000)


class CursorPagination(pagination.CursorPagination):
    page_size = PAGE_SIZE
    max_page_size = PAGE_SIZE_MAX


class LimitOffsetPagination(pagination.LimitOffsetPagination):
    default_limit = PAGE_SIZE
    max_limit = PAGE_SIZE_MAX


class PageNumberPagination(pagination.PageNumberPagination):
    page_size = PAGE_SIZE
    max_page_size = PAGE_SIZE_MAX
