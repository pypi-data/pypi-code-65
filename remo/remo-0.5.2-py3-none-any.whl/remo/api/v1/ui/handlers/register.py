import json
import logging

from rest_framework import viewsets, status
from rest_framework.response import Response

from remo_app.remo.services import users
from remo_app.remo.services import license
from remo_app.remo.services.email import send_email, compose_msg

logger = logging.getLogger('remo_app')


class Register(viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        return Response({})

    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({'error': 'not allowed action'}, status=status.HTTP_403_FORBIDDEN)

        try:
            data = json.loads(request.body)
            data = data.get('user', {})
        except Exception:
            return Response({'error': 'failed to parse payload'}, status=status.HTTP_400_BAD_REQUEST)

        email, username, fullname, company, allow_marketing_emails = (
            data.get('email', ''),
            data.get('username', ''),
            data.get('fullname', ''),
            data.get('company', ''),
            data.get('allow_marketing_emails', False),
        )

        if not email:
            return Response({'error': 'email was not set'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            users.create_or_update_superuser(email=email,
                                             username=username,
                                             fullname=fullname,
                                             company=company,
                                             allow_marketing_emails=allow_marketing_emails)
        except Exception as err:
            return Response({'error': f'failed to update user details: {err}'}, status=status.HTTP_400_BAD_REQUEST)

        ok, req, resp = license.register_user(email=email,
                                              username=username,
                                              fullname=fullname,
                                              company=company,
                                              allow_marketing_emails=allow_marketing_emails)
        if not ok:
            send_email(
                subject=f'Failed to register user from UI: {fullname}',
                content=compose_msg(req, resp)
            )
            return Response({'error': 'failed to register user'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({}, status=status.HTTP_200_OK)
