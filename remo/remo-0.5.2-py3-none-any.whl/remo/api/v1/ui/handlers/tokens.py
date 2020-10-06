import json

from rest_framework import viewsets, status
from rest_framework.response import Response

from remo_app.remo.services.license import store_token


class Tokens(viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        return Response({})

    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({'error': 'not allowed action'}, status=status.HTTP_403_FORBIDDEN)

        try:
            data = json.loads(request.body)
        except Exception:
            return Response({'error': 'failed to parse payload'}, status=status.HTTP_400_BAD_REQUEST)

        token = data.get('token', '')
        if not token:
            return Response({'error': 'token was not set'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'valid': store_token(token)}, status=status.HTTP_200_OK)
