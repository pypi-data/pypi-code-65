import json
import logging
import re
import unicodedata

import requests
import warnings
from datetime import datetime

from django.contrib.auth import get_user_model

from rest_framework import viewsets, status
from rest_framework.response import Response

logger = logging.getLogger('remo_app')


class Users(viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        return Response({})

    def create(self, request, *args, **kwargs):
        return Response({'error': 'not allowed action'}, status=status.HTTP_403_FORBIDDEN)

        if not request.user.is_superuser:
            return Response({'error': 'not allowed action'}, status=status.HTTP_403_FORBIDDEN)

        try:
            data = json.loads(request.body)
        except Exception:
            return Response({'error': 'failed to parse payload'}, status=status.HTTP_400_BAD_REQUEST)

        email, password, username, full_name = (
            data.get('email', ''),
            data.get('password', ''),
            data.get('username', ''),
            data.get('full_name', ''),
        )
        if not email or not password:
            return Response({'error': 'email or password was not set'}, status=status.HTTP_400_BAD_REQUEST)

        if not self.create_remo_user(email, password, username, full_name):
            return Response({'error': 'user already exists'}, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_201_CREATED)

    def create_remo_user(self, email: str, password: str, username: str, full_name: str) -> bool:
        email, username, first_name, last_name = self.normalize_user_info(email, username, full_name)

        User = get_user_model()
        user = User.objects.filter(email=email)
        warnings.simplefilter("ignore")
        if user.exists():
            return False

        user = User.objects.create_user(username, email, password, last_login=datetime.now())
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return True

    def normalize_user_info(self, email: str, username: str, full_name: str):
        first_name, last_name = self.split_full_name(full_name)

        username = self.normalize_username(username)
        if not username:
            username = self.normalize_username(first_name)
        if not username:
            username = self.normalize_username(email.split('@', 1)[0])

        email = email.lower()
        return email, username, first_name, last_name

    @staticmethod
    def normalize_username(username: str) -> str:
        if isinstance(username, str):
            username = re.sub(r"[\s-]+", "_", username.lower())
            username = re.sub(r"[^.\w\d_]+", "", username)
            return unicodedata.normalize('NFKC', username)
        return ''

    @staticmethod
    def split_full_name(full_name: str) -> (str, str):
        first_name, last_name = '', ''
        full_name = full_name.strip().split(' ', 1)
        if len(full_name) == 2:
            first_name, last_name = full_name
        else:
            first_name = full_name[0]
        return first_name, last_name
