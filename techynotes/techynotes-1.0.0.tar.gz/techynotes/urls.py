from django.urls import path

from . import views

urlpatterns = [
     path('', views.home, name='home'),
     path('loadnote', views.loadnote, name='loadnote'),
     path('search_user', views.search_user, name='search_user'),
     path('save_file', views.save_file, name="save_file"),
     path('fetch_user_notes', views.fetch_user_notes, name="fetch_user_notes"),
     path('login', views.login, name="login"),
     path('logout', views.logout, name="logout"),     
]