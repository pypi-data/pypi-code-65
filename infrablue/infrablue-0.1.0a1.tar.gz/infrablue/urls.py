from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views import generic
from django.views.generic import TemplateView

from bigbluebutton.django.urls import urlpatterns as bbb_urls
from two_factor.urls import urlpatterns as tf_urls

from . import views

urlpatterns = [
    path("", include(bbb_urls)),
    path("", include(tf_urls)),
    path("", views.index, name="index"),
    path("account/", include("django_registration.backends.activation.urls")),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("admin/", admin.site.urls),
    path(
        "preferences/site/", views.preferences, {"registry_name": "site"}, name="preferences_site"
    ),
    path(
        "preferences/person/",
        views.preferences,
        {"registry_name": "person"},
        name="preferences_person",
    ),
    path(
        "preferences/group/",
        views.preferences,
        {"registry_name": "group"},
        name="preferences_group",
    ),
    path(
        "preferences/site/<int:pk>/",
        views.preferences,
        {"registry_name": "site"},
        name="preferences_site",
    ),
    path(
        "preferences/person/<int:pk>/",
        views.preferences,
        {"registry_name": "person"},
        name="preferences_person",
    ),
    path(
        "preferences/group/<int:pk>/",
        views.preferences,
        {"registry_name": "group"},
        name="preferences_group",
    ),
    path(
        "preferences/site/<int:pk>/<str:section>/",
        views.preferences,
        {"registry_name": "site"},
        name="preferences_site",
    ),
    path(
        "preferences/person/<int:pk>/<str:section>/",
        views.preferences,
        {"registry_name": "person"},
        name="preferences_person",
    ),
    path(
        "preferences/group/<int:pk>/<str:section>/",
        views.preferences,
        {"registry_name": "group"},
        name="preferences_group",
    ),
    path(
        "preferences/site/<str:section>/",
        views.preferences,
        {"registry_name": "site"},
        name="preferences_site",
    ),
    path(
        "preferences/person/<str:section>/",
        views.preferences,
        {"registry_name": "person"},
        name="preferences_person",
    ),
    path(
        "preferences/group/<str:section>/",
        views.preferences,
        {"registry_name": "group"},
        name="preferences_group",
    ),
    path("m/<slug>/", views.MeetingJoin.as_view(), name="meeting_join_short", ),
    path("me/", views.SelfDetailView.as_view(), name="self_detail",),
    path("me/change_password/", views.UserChangePassword.as_view(), name="self_change_password",),
    path("meeting/", views.MeetingList.as_view(), name="meeting_list", ),
    path("meeting/create/", views.MeetingCreate.as_view(), name="meeting_create", ),
    path("meeting/<pk>/", views.MeetingDetail.as_view(), name="meeting_detail", ),
    path("meeting/<pk>/update/", views.MeetingUpdate.as_view(), name="meeting_update", ),
    path("meeting/<pk>/delete/", views.MeetingDelete.as_view(), name="meeting_delete", ),
    path("meeting/join/<slug>/", views.MeetingJoin.as_view(), name="meeting_join", ),
    path("meeting/join/id/<pk>/", views.MeetingJoinID.as_view(), name="meeting_join_id", ),
    path("meetingurl/<pk>/delete/", views.MeetingURLDelete.as_view(), name="meetingurl_delete", ),
    path("user/", views.UserList.as_view(), name="user_list",),
    path("user/create/", views.UserCreate.as_view(), name="user_create",),
    path("user/<pk>/update/", views.UserUpdate.as_view(), name="user_update",),
    path("user/<pk>/delete/", views.UserDelete.as_view(), name="user_delete",),
    path("user/<pk>/detail/", views.UserDetail.as_view(), name="user_detail",),
    path("user/<pk>/change_password/", views.UserChangePassword.as_view(), name="user_change_password", ),
    path("group/", views.GroupList.as_view(), name="group_list",),
    path("group/create/", views.GroupCreate.as_view(), name="group_create",),
    path("group/<pk>/update/", views.GroupUpdate.as_view(), name="group_update",),
    path("group/<pk>/delete/", views.GroupDelete.as_view(), name="group_delete",),
    path("group/<pk>/detail/", views.GroupDetail.as_view(), name="group_detail",),
    path("server_group/", views.ServerGroupList.as_view(), name="server_group_list",),
    path("server_group/create/", views.ServerGroupCreate.as_view(), name="server_group_create",),
    path(
        "server_group/<pk>/update/", views.ServerGroupUpdate.as_view(), name="server_group_update",
    ),
    path(
        "server_group/<pk>/delete/", views.ServerGroupDelete.as_view(), name="server_group_delete",
    ),
]

if "social_django" in settings.INSTALLED_APPS:
    from social_django.urls import urlpatterns as social_urls  # noqa

    urlpatterns += [path("", include(social_urls))]

# Add URLs for optional features
if hasattr(settings, "TWILIO_ACCOUNT_SID"):
    from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls  # noqa

    urlpatterns += [path("", include(tf_twilio_urls))]
