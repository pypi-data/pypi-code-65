"""Urls for trips app"""
from django.conf.urls import include
from django.urls import path

urlpatterns = [
    path('api/', include('django_trips.api.urls')),

]
