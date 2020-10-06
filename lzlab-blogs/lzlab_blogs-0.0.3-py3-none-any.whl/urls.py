import django
from django.conf import settings
from django.conf.urls.static import static

from lzlab_blogs.extensions.mdeditor.views import UploadView

if django.VERSION[0] > 1:
    from django.urls import re_path as url_func
else:
    from django.conf.urls import url as url_func

urlpatterns = [
    url_func(r'^mdeditor/uploads/$', UploadView.as_view(), name='uploads')
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
