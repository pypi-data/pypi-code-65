from mapbox_baselayer.models import MapBaseLayer
from rest_framework.serializers import ModelSerializer


class BaseLayerSerializer(ModelSerializer):

    class Meta:
        model = MapBaseLayer
        field = "__all__"
