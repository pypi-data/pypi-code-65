# pylint: disable=E0611
"""Declares :class:`Blob`."""
import json

from django.db import models
from django.utils.translation import gettext_lazy as _
from unimatrix.lib import timezone


class Blob(models.Model):
    """Maintains information about blobs used by an application."""

    #: SHA-256 hash of the blob content.
    checksum = models.CharField(
        max_length=64,
        verbose_name=_("Checksum"),
        blank=False,
        null=False,
        unique=True,
        db_column='checksum'
    )

    #: Date and time at which the :class:`Blob` was created, in milliseconds
    #: since the UNIX epoch.
    created = models.BigIntegerField(
        verbose_name=_("Created"),
        blank=False,
        null=False,
        default=timezone.now,
        db_column='created'
    )

    #: If known, the content type of the :class:`Blob`.
    content_type = models.CharField(
        verbose_name=_("Content Type"),
        max_length=64,
        blank=False,
        null=False,
        default="application/octet-stream",
        db_column='content_type'
    )

    #: The size of the blob, in bytes. The default value is ``0`` so we can
    #: create the database entity prior to uploading.
    length = models.BigIntegerField(
        verbose_name=_("Size"),
        blank=False,
        null=False,
        default=0,
        db_column='length'
    )

    #: Mapping of key/value pairs providing extra context for this specific
    #: :class:`Blob`. All keys and values must be strings.
    labels = models.JSONField(
        verbose_name=_("Labels"),
        blank=False,
        null=False,
        default=dict,
        db_column='labels'
    )

    def setlabels(self, labels):
        """Sets the labels on the :class:`Blob` instance."""
        if isinstance(labels, str):
            labels = json.loads(labels)
        self.labels = labels

    def getlabels(self):
        """Return the labels specified for this :class:`Blob`."""
        labels = self.labels
        if isinstance(labels, str):
            labels = json.loads(labels)
        return labels

    __module__ = 'unimatrix.ext.octet.models'

    class Meta: # pylint: disable=C0115,R0903
        app_label = 'octet'
        db_table = 'blobs'
        default_permissions = []
        verbose_name = _("Blob")
        verbose_name_plural = _("Blobs")
