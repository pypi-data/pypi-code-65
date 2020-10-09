import uuid
from typing import TYPE_CHECKING, List, Union

from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from ..api.attendee import Attendee, Role

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.auth.models import AnonymousUser

    from .models import Meeting

    User = get_user_model()


def get_user_id(user: Union["AnonymousUser", "User"]) -> str:
    """Get a unique ID for a Django user.

    If the User object has a guid attribute, this is used by default. If not,
    the primary key is used as a fallback.

    It can be overridden with the `BBB_USER_ID_CALLBACK` setting.
    """

    if user.is_anonymous:
        return str(uuid.uuid1())
    else:
        return str(getattr(user, "guid", user.pk))


def get_display_name(user: Union["AnonymousUser", "User"]) -> str:
    """Get a display namefor a Django user.

    Defaults to the full name of the user object or, if it is empty, its
    user name.

    It can be overridden with the `BBB_DISPLAY_NAME_CALLBACK` setting.
    """

    if user.is_anonymous:
        return user.username or _("Anonymous User")
    else:
        return user.get_full_name().strip() or user.username


def get_meeting_id(meeting: "Meeting") -> str:
    """Get a unique ID for a meeting from its Django object.

    This method returns the guid field of the meeting object and is used by default.

    It can be overridden with the `BBB_MEETING_ID_CALLBACK` setting.
    """
    return str(meeting.guid)


def get_attendee(user: Union["AnonymousUser", "User"], meeting: "Meeting") -> Attendee:
    """Generate an Attendee object for a meeting and user.

    If the user's ID is already a known attendee on the meeting by the information
    known to the API, the object is returned. If not, a new one is created.

    It can be overridden with the `BBB_ATTENDEE_CALLBACK` setting.
    """
    for attendee in meeting.meeting.attendees.values():
        if attendee.user_id == user.bbb_user_id:
            # Attendee with same user ID found
            return attendee

    # No attendee found, generate new one
    attendee = Attendee(
        meeting.meeting,
        user_id=user.bbb_user_id,
        full_name=user.bbb_display_name,
        role=user.bbb_get_role(meeting),
    )
    return attendee


def get_role(user: Union["AnonymousUser", "User"], meeting: "Meeting") -> Role:
    """Determine the role of a user for a meeting.

    By default, staff members and superusers become moderators, all other users
    become viewers. Developers integrating BigBlueButton in their project are
    strongly advised to override this behaviour with proper permission checking.

    It can be overridden with the `BBB_ROLE_CALLBACK` setting.
    """
    if user.is_superuser or user.is_staff:
        return Role.MODERATOR
    else:
        return Role.VIEWER


def get_user_attendees(user: Union["AnonymousUser", "User"]) -> List[Attendee]:
    from .models import BigBlueButtonGroup  # noqa

    attendees = []

    for group in BigBlueButtonGroup.on_site.all():
        # FIXME Use meetings property after it was turned into cached live data
        for meeting in group.api_group.get_meetings().values():
            for attendee in meeting.attendees.values():
                if attendee.user_id == user.bbb_user_id:
                    attendees.append(attendee)

    return attendees
