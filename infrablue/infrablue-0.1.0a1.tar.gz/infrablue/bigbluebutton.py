from django.core.exceptions import PermissionDenied

from bigbluebutton.api import Role
from typing import Union


def get_role(user: Union["AnonymousUser", "User"], meeting: "Meeting") -> Role:
    """Determine the role of a user for a meeting based on a permission granted in the view function.
    """

    from guardian.shortcuts import get_perms, remove_perm

    permissions = get_perms(user, meeting)

    if user.is_anonymous:
        for permission in permissions:
            remove_perm(permission, user, meeting)

    if "join_as_moderator" in permissions:
        return Role.MODERATOR
    elif "join_as_attendee" in permissions:
        return Role.VIEWER
    else:
        raise PermissionDenied()


MEETING_METADATA = {
    "Recording": [
        ("record", "record_voice_over,voice_over_off"),
        ("auto_start_recording", "sync,sync_disabled"),
        ("allow_start_stop_recording", "toggle_on,toggle_off"),
    ],
    "Webcam": [

        ("enable_cam", "videocam,videocam_off"),
        ("webcams_only_for_moderator", "toggle_on,toggle_off"),
    ],
    "Microphone": [

        ("enable_mic", "mic,mic_off"),
        ("mute_on_start", "volume_mute,volume_up"),
        ("allow_mods_to_unmute_users", "hearing,hearing_disabled"),
    ],
    "Additional Features ": [

        ("enable_private_chat", "chat,speaker_notes_off"),
        ("enable_public_chat", "chat,speaker_notes_off"),
        ("enable_note", "note,label_off")
    ]
}
