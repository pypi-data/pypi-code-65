from rest_framework import viewsets, status
from rest_framework.response import Response

from remo_app.remo.services.license import read_license


class License(viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        return Response(read_license(), status=status.HTTP_200_OK)
