"""Declares :class:`BlobView`."""
import ioc


class BlobView:
    """Provides request handlers to download the content of :class:`Blob`
    instances.
    """
    auth = ioc.class_property('BlobRequestAuthorizationService')

    async def __call__(self, request):
