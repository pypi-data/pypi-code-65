from django.urls import path, include
from akeru.views import AWSConsoleView, AccessView, IndexView

urlpatterns = [
    path('console/<type>/<entity_name>/', AWSConsoleView.as_view(),
         name='console-view'),
    path('access/', AccessView.as_view(), name='access-role-list'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', IndexView.as_view(), name='index')
]
