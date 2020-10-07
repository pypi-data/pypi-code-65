from django.urls import path

from .views import APIView

urlpatterns = [
    path("api/<str:method>", APIView.as_view(), name="api_request"),
]
