from rest_framework import viewsets

from .mixins import (
    AtomicMixin,
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)


class GenericViewSet(
    AtomicMixin,
    viewsets.GenericViewSet,
):
    pass


class ReadOnlyModelViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    pass


class ModelViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    pass
