from django.urls import path
from . import views

urlpatterns = [
    path('timerboard/timer/add/', views.add_timer, name="django-eveonline-timerboard-timer-add"),
    path('timerboard/timer/remove/<int:pk>/', views.remove_timer, name="django-eveonline-timerboard-timer-remove"),
    path('timerboard/view/', views.view_timerboard, name="django-eveonline-timerboard-view"),
]
