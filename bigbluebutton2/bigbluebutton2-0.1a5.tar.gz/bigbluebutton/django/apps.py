from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from . import settings, util


class BigbluebuttonConfig(AppConfig):
    name = "bigbluebutton.django"
    verbose_name = _("BigBlueButton Django integration")
    label = "bigbluebutton"

    def ready(self):
        """Extend the User model with attribute shortcuts."""

        from django.contrib.auth.models import AnonymousUser  # noqa

        User = get_user_model()

        User.add_to_class("bbb_attendees", property(util.get_user_attendees))
        User.add_to_class("bbb_user_id", property(settings.USER_ID_CALLBACK))
        User.add_to_class("bbb_display_name", property(settings.DISPLAY_NAME_CALLBACK))
        User.add_to_class("bbb_get_attendee", settings.ATTENDEE_CALLBACK)
        User.add_to_class("bbb_get_role", settings.ROLE_CALLBACK)

        setattr(AnonymousUser, "bbb_attendees", property(util.get_user_attendees))
        setattr(AnonymousUser, "bbb_user_id", property(settings.USER_ID_CALLBACK))
        setattr(AnonymousUser, "bbb_display_name", property(settings.DISPLAY_NAME_CALLBACK))
        setattr(AnonymousUser, "bbb_get_attendee", settings.ATTENDEE_CALLBACK)
        setattr(AnonymousUser, "bbb_get_role", settings.ROLE_CALLBACK)
