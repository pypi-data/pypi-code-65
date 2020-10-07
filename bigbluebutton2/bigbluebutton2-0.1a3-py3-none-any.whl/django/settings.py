"""Aggregated and seeded settings for the bigbluebutton integration app"""

from django.conf import settings as _settings
from django.utils.module_loading import import_string

AUTH_USER_MODEL = _settings.AUTH_USER_MODEL

_PREFIX = "BBB"

ATTENDEE_CALLBACK = import_string(
    getattr(_settings, f"{_PREFIX}_ATTENDEE_CALLBACK", "bigbluebutton.django.util.get_attendee")
)
MEETING_ID_CALLBACK = import_string(
    getattr(_settings, f"{_PREFIX}_MEETING_ID_CALLBACK", "bigbluebutton.django.util.get_meeting_id")
)
DISPLAY_NAME_CALLBACK = import_string(
    getattr(
        _settings, f"{_PREFIX}_DISPLAY_NAME_CALLBACK", "bigbluebutton.django.util.get_display_name"
    )
)
USER_ID_CALLBACK = import_string(
    getattr(_settings, f"{_PREFIX}_USER_ID_CALLBACK", "bigbluebutton.django.util.get_user_id")
)
ROLE_CALLBACK = import_string(
    getattr(_settings, f"{_PREFIX}_ROLE_CALLBACK", "bigbluebutton.django.util.get_role")
)

CACHE_NAME = getattr(_settings, f"{_PREFIX}_CACHE_NAME", "default")
