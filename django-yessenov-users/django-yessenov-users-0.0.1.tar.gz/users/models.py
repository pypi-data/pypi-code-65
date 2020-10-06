from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name=_('email'))
    middle_name = models.CharField(blank=True, max_length=150, verbose_name=_('middle name'))
    identify_code = models.CharField(blank=True, max_length=12, verbose_name=_('identify code'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email