from django.urls import path
from rest_framework.routers import SimpleRouter
from terra_settings.views import SettingsView, BaseLayerViewSet

app_name = 'terra_settings'

router = SimpleRouter()
router.register('baselayer', BaseLayerViewSet, basename='baselayer')

urlpatterns = [
    path('settings/', SettingsView.as_view(), name='settings'),
] + router.urls
