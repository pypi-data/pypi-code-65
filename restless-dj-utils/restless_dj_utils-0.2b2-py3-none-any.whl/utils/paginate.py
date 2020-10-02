"""
Utils for paginating objects in restless. This is used by PaginateResourceMixin
"""
import typing as t
import dataclasses as d

from django.db import models


@d.dataclass
class Paginated:
    """Represents paginated objects"""

    objects: t.Any
    total: int
    page: int
    limit: int


def pagination_input(request, default_limit=10, max_limit=100):
    """
    Get pagination data needed to pass to backend for pagination
    """

    page = request.GET.get("page", 1)
    limit = request.GET.get("limit", default_limit)

    # default value does not ensure that param is valid or convertible to int
    try:
        page = abs(int(page))
    except ValueError:
        page = 1
    try:
        limit = abs(int(limit))
    except ValueError:
        limit = default_limit

    if limit > max_limit:
        limit = max_limit
    start = (page * limit) - limit
    return start, page, limit


def paginate(objects, request, default_limit=10, max_limit=100):
    """
    Simple helper for paginating QuerySets in Restless.
    """

    start, page, limit = pagination_input(request, default_limit, max_limit)
    if isinstance(objects, models.query.QuerySet):
        total = objects.count()
    else:
        total = len(objects)
    end = min([page * limit, total])
    return Paginated(objects[start:end], total, page, limit)
