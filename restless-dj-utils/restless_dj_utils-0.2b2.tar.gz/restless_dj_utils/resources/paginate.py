"""
Paginate resource mixin
"""
from restless_dj_utils.utils.paginate import Paginated


class PaginateResourceMixin:
    """Paginate resource mixin"""

    wrap_list = True

    def serialize_list(self, data):
        """
        Override serialize_list to return extra data for paginated results
        """

        if isinstance(data, Paginated):
            final_data = self.serialize_paginated(data)
            return self.serializer.serialize(final_data)

        return super().serialize_list(data)

    def serialize_paginated(self, data):
        """
        Helper method for serializing paginated objects
        :param data: Paginated object
        :return: Dictionary of paginated object
        """

        self.wrap_list = False
        return {
            "objects": self._prepare_list(data.objects),
            "page": data.page,
            "total": data.total,
            "limit": data.limit,
        }

    def _prepare_list(self, data):
        if data is None:
            return []

        # Check for a ``Data``-like object. We should assume ``True`` (all
        # data gets prepared) unless it's explicitly marked as not.
        if not getattr(data, "should_prepare", True):
            prepped_data = data.value
        else:
            prepped_data = [self.prepare(item) for item in data]
        return prepped_data

    def wrap_list_response(self, data):
        """Wrap data if self.wrap_list is set"""
        if self.wrap_list:
            return super().wrap_list_response(data)

        return data
