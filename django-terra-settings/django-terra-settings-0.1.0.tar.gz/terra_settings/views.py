from django.conf import settings
from mapbox_baselayer.models import MapBaseLayer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from terra_settings.serializers import BaseLayerSerializer
from terra_settings.settings import TERRA_APPLIANCE_SETTINGS


class SettingsView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        terra_settings = {
            # TODO: move this after terracommon.accounts split
            'jwt_delta': settings.JWT_AUTH['JWT_EXPIRATION_DELTA'],
            'base_layers': BaseLayerSerializer(MapBaseLayer.objects.all(), many=True).data,
        }

        terra_settings.update(TERRA_APPLIANCE_SETTINGS)

        return Response(terra_settings)


class BaseLayerViewSet(ModelViewSet):
    serializer_class = BaseLayerSerializer
    queryset = MapBaseLayer.objects.all()
