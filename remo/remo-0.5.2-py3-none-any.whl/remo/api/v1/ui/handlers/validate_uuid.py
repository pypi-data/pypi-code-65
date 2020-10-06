from datetime import timedelta

import json
import logging

from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from remo_app.remo.models.downloads import AgrInstallations, AgrUsage

logger = logging.getLogger('remo_app')


class ValidateUUID(viewsets.GenericViewSet):
    permission_classes = (AllowAny,)

    def list(self, request, *args, **kwargs):
        return Response({})

    @staticmethod
    def parse_payload(request):
        try:
            data = json.loads(request.body)
        except Exception:
            return Response({'error': 'failed to parse payload'}, status=status.HTTP_400_BAD_REQUEST), None

        return None, data

    def parse_uuid(self, request):
        err, data = self.parse_payload(request)
        if err:
            return err, None

        uuid = data.get('uuid')
        if not uuid:
            return Response({'error': 'failed to parse uuid'}, status=status.HTTP_400_BAD_REQUEST), None

        return None, uuid

    @staticmethod
    def is_uuid_valid(uuid: str) -> bool:
        return AgrInstallations.objects.filter(uuid=uuid).exists() or AgrUsage.objects.filter(uuid=uuid).exists()

    def create(self, request, *args, **kwargs):
        err, uuid = self.parse_uuid(request)
        if err:
            return err

        return Response(
            {'valid': self.is_uuid_valid(uuid)}, status=status.HTTP_200_OK
        )

    @action(['post'], detail=True, url_path='trial')
    def trial(self, request, pk=None):
        err, uuid = self.parse_uuid(request)
        if err:
            return err

        if not self.is_uuid_valid(uuid):
            return Response({'valid': False}, status=status.HTTP_200_OK)

        total_usage = timedelta(minutes=0)
        for usage in AgrUsage.objects.filter(uuid=uuid).all():
            duration = usage.overall_duration if usage.overall_duration else usage.actual_usage
            if not duration:
                duration = timedelta(minutes=0)
            total_usage += duration

        return Response({'valid': total_usage < timedelta(hours=8)}, status=status.HTTP_200_OK)
