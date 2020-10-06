from django.conf import settings
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from appchance.client.ftp import ClientSFTP


class PickupPointDPD(models.Model):
    ext_id = models.CharField(_("external id"), max_length=7)
    post_code = models.CharField(_("postal code"), max_length=6)
    address = models.CharField(_("address"), max_length=100)
    opening_hours = models.TextField(_("opening hours"))
    is_active = models.BooleanField(_("is active"), default=True)
    location = PointField(_("location"))
    additional_info = models.CharField(_("additional information"), max_length=250, blank=True)
    update_dt = models.DateTimeField(_("update"), null=True, blank=True)

    class Meta:
        abstract = True

    @staticmethod
    def fetch_pickup_points():
        sftp = ClientSFTP(settings.DPD_SFTP_HOST, settings.DPD_SFTP_PORT, settings.DPD_SFTP_USER, settings.DPD_SFTP_PASSWORD)
        sftp.get_latest(settings.DPD_SFTP_REMOTE_PATH, settings.DPD_SFTP_LOCAL_PATH)

    @classmethod
    def update_pickup_points(cls):
        with open(settings.DPD_SFTP_LOCAL_PATH, "r") as csv_file:
            next(csv_file)
            for line in csv_file:
                columns = line.split(";")
                if columns[0] != "\n" and columns[1][:2] in ["PL"]:
                    point, crtd = cls.objects.get_or_create(ext_id=columns[1], defaults={
                        "post_code": columns[2],
                        "address": "{} {}".format(columns[4], columns[7]),
                        "opening_hours": columns[10],
                        "location": Point([float(columns[14]), float(columns[13])]),
                        "additional_info": columns[15],
                    })
                    point.is_active = True if columns[11] == "Aktywny" else False
                    point.update_dt = timezone.now()
                    point.save(update_fields=["is_active"])

    @classmethod
    def fetch_and_update(cls):
        cls.fetch_pickup_points()
        cls.update_pickup_points()
