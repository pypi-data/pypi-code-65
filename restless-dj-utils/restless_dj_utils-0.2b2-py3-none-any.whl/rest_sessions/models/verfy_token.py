"""
Token model and manager
"""
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone

from restless_dj_utils.rest_sessions.conf import TOKEN_MAX_AGE


class VerifyTokenManager(models.Manager):
    """Token manager"""

    def get_active(self, token):
        """
        Get active token
        :param token:
        :return:
        """

        start = timezone.now() - timedelta(seconds=TOKEN_MAX_AGE)
        return self.get_queryset().get(token=token, created__gte=start)


class VerifyToken(models.Model):
    """Token for user to verify their account"""

    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verify_tokens",
    )
    token = models.CharField(max_length=32, default="")

    objects = VerifyTokenManager()

    class Meta:
        ordering = ["-created"]
        verbose_name = "Verify Token"
        verbose_name_plural = "Verify Tokens"
        app_label = "rest_sessions"

    def __str__(self):
        return f"Verify token for {self.user}"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(length=32)
        return super().save(*args, **kwargs)
