from django.urls import path

from .views import APIView

urlpatterns = [
    path("api/<str:method>", APIView.as_view()),
    path("api", APIView.as_view()),
]
