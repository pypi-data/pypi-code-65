from django.db import transaction
from rest_framework import mixins
# from rest_framework_extensions import mixins as mixins_ext

from .exceptions import Success
from .settings import (
    MB_EXCEPTIONS,
    MB_VIEWS,
)


class AtomicMixin(object):
    atomic_actions = MB_VIEWS.get(
        'ATOMIC_ACTIONS', [
            'create',
            'update',
            'destroy',
            'post',
            'put',
            'patch',
            'delete',
        ]
    )
    atomic_enabled = bool(
        MB_VIEWS.get('ATOMIC_ENABLED', False))
    atomic_savepoint = bool(
        MB_VIEWS.get('ATOMIC_SAVEPOINT', True))

    def __init__(self, *args, **kwargs):
        self.patch_actions()

    def patch_actions(self):
        if not self.atomic_enabled:
            return  # do nothing if atomic is not enabled

        if not self.atomic_actions:
            dispatch_method = getattr(self, 'dispatch', None)
            if callable(dispatch_method):
                setattr(
                    self,
                    'dispatch',
                    transaction.atomic(
                        dispatch_method,
                        savepoint=self.atomic_savepoint,
                    )
                )

        else:
            for action in self.atomic_actions:
                action_method = getattr(self, action, None)
                if callable(action_method):
                    setattr(
                        self,
                        action,
                        transaction.atomic(
                            action_method,
                            savepoint=self.atomic_savepoint,
                        ),
                    )

    @classmethod
    def as_view(cls, *args, **kwargs):
        as_view_method = getattr(super(), 'as_view', None)
        if not callable(as_view_method):
            raise AssertionError('no as_view method found')

        view = as_view_method(*args, **kwargs)
        return (
            transaction.non_atomic_requests(view) if
            cls.atomic_enabled else view
        )


class ResponseMixin(object):
    error_return = Success()
    error_return_ensured = bool(
        MB_EXCEPTIONS.get('ERROR_RETURN_ENSURED', False))

    def get_response(self, resp):
        if self.error_return_ensured:
            resp.data = self.error_return.get_data(resp.data)
        return resp


class CreateModelMixin(
    ResponseMixin,
    mixins.CreateModelMixin,
):

    def create(self, request, *args, **kwargs):
        return self.get_response(
            super().create(request, *args, **kwargs))


class DestroyModelMixin(
    ResponseMixin,
    mixins.DestroyModelMixin,
):

    def destroy(self, request, *args, **kwargs):
        return self.get_response(
            super().destroy(request, *args, **kwargs))


class UpdateModelMixin(
    ResponseMixin,
    mixins.UpdateModelMixin,
):

    def update(self, request, *args, **kwargs):
        return self.get_response(
            super().update(request, *args, **kwargs))


class ListModelMixin(
    ResponseMixin,
    mixins.ListModelMixin,
):

    def list(self, request, *args, **kwargs):
        return self.get_response(
            super().list(request, *args, **kwargs))


class RetrieveModelMixin(
    ResponseMixin,
    mixins.RetrieveModelMixin,
):

    def retrieve(self, request, *args, **kwargs):
        return self.get_response(
            super().retrieve(request, *args, **kwargs))


# class NestedViewSetMixin(mixins_ext.NestedViewSetMixin):
#
#     def get_parents_query_dict_ex(self, ignore_prefix=None):
#         if not ignore_prefix:
#             return self.get_parents_query_dict()
#
#         return {
#             (
#                 k[len(ignore_prefix):] if
#                 k.startswith(ignore_prefix) else k
#             ): v for k, v in self.get_parents_query_dict().items()
#         }
