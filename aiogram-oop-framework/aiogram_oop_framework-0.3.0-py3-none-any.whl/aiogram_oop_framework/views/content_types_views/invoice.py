from aiogram.types import ContentType

from .base import BaseContentTypesView


class InvoiceView(BaseContentTypesView):
    """Same as :class:`aiogram_oop_framework.views.content_types_views.animation.AnimationView`, but content_types defaults to [ContentType.INVOICE]"""
    content_types = [ContentType.INVOICE]
