from rest_framework import viewsets, status
from rest_framework.response import Response

from remo_app.remo.services.license import is_trial_valid


class ValidateTrial(viewsets.GenericViewSet):

    def list(self, request, *args, **kwargs):
        return Response({'valid': is_trial_valid()}, status=status.HTTP_200_OK)
