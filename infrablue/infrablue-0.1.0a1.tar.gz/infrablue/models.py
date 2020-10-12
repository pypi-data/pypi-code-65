from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _

from dynamic_preferences.models import PerInstancePreferenceModel
from uuid import uuid4

from bigbluebutton.django.models import Meeting


class SitePreferenceModel(PerInstancePreferenceModel):
    """Preference model to hold pereferences valid for a site."""

    instance = models.ForeignKey(Site, on_delete=models.CASCADE)

    class Meta:
        app_label = "infrablue"


class GroupPreferenceModel(PerInstancePreferenceModel):
    """Preference model to hold pereferences valid for members of a group."""

    instance = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        app_label = "infrablue"


class MeetingURL(models.Model):
    """A URL assignment for a :class:`Meeting` object.

    Each meeting can have an arbitrary set of URLs assigned.
    They have a role assigned, which defines the access level
    a user that is not logged in gets when joining the meeting.
    If the user is logged in, they can of course escalate their
    privileges to whatever their account allows.

    A URL can also have a separate attendee and/or moderator
    password assigned, which is required to join the meeting through
    the web UI, in the following order:

     - If the default_role is set, the according privileges are always
       granted, without a password
     - If the default_role is not set, or it is set to VIEWER, but a
       moderator password is set, it can be optionally entered to escalate
       privileges
     - If the user is logged in, they do not need a password to gain privileges
       on this meeting that they already assume through permissions
     - A logged in user can use a password to escalate their privileges beyond
       those they assume through permissions
    """

    DEFAULT_ROLE_CHOICES = (
        ("VIEWER", _("Viewer")),
        ("MODERATOR", _("Moderator")),
    )

    meeting = models.ForeignKey(
        Meeting, on_delete=models.CASCADE, related_name="urls", verbose_name=_("Meeting")
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_("URL name for the meeting"),
    )

    default_role = models.CharField(
        max_length=9,
        choices=DEFAULT_ROLE_CHOICES,
        verbose_name=_("Default role for unauthenticated users"),
    )

    attendee_pw = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Attendee password"),
        help_text=_("Password used to gain additional viewer permissions"),
    )
    moderator_pw = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Moderator password"),
        help_text=_("Password used to gain additional moderator permissions"),
    )

    def save(self, *args, **kwargs):
        """
        The overriding of the save method is needed, due to the inline_formsets
        """
        if not self.slug:
            self.slug = uuid4()
        return super().save(*args, **kwargs)
