"""Data structures for manageing meeting attendees"""

import logging
import webbrowser
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

from ._caching import cache
from .util import camel_to_snake, snake_to_camel, to_field_type

if TYPE_CHECKING:  # pragma: no cover
    from .meeting import Meeting

logger = logging.getLogger(__name__)


class Role(Enum):
    """Enumeration of roles an attendee can have"""

    MODERATOR = "MODERATOR"
    VIEWER = "VIEWER"
    DIAL_IN_USER = "DIAL-IN-USER"


@dataclass
class Attendee:
    """One attendee that participates in one meeting.

    This object holds the information about one participant and is linked to
    exactly one meeting.
    """

    meeting: "Meeting"  # noqa: F821
    full_name: str
    user_id: Optional[str] = None
    role: Optional[Role] = field(default=None, compare=False)
    is_presenter: bool = field(default=False, compare=False)
    is_listening_only: bool = field(default=False, compare=False)
    has_joined_voice: bool = field(default=False, compare=False)
    has_video: bool = field(default=False, compare=False)
    client_type: Optional[str] = field(default=None, compare=False)

    auth_token: Optional[str] = field(default=None, compare=False, init=False)
    session_token: Optional[str] = field(default=None, compare=False, init=False)
    url: Optional[str] = field(default=None, compare=False, init=False)

    def __post_init__(self):
        """Self-register in linked meeting."""
        self.meeting.attendees[self.full_name] = self

    def join(
        self, browser: bool = False, do_join: bool = True, do_create: bool = False
    ) -> Optional[str]:
        """Join an attendee corresponding to this object into the meeting it is linked to.

        To request the join, this method can either call the API directly and return the URL to
        the (HTML5) client, or only construct the API call URL and then hand it off to the
        default browser (if the browser argument is set to True) or return it plain without
        calling (if the do_join argument is set to False).

        The meeting is created before joining if `do_create` is set to `True`.

        In BigBlueButton's default configuration, in addition to the session token in the client
        URL, a valid JSESSIONID cookie is required, so using the client URL outside the original
        request scope only works if the server supports it.
        """
        logger.info(
            f"Joining meeting {self.meeting.meeting_id} on server {self.meeting.api.name} "
            f"as {self.full_name}, role {self.role}"
        )

        # Update and, if requested, create the meeting before joining to get current information
        if do_create:
            self.meeting.create()
        self.meeting.get_meeting_info()

        url_args: Dict[str, str] = {}

        if not self.meeting.meeting_id:
            raise ValueError("Cannot join meeting with unknown ID.")
        url_args["meetingID"] = self.meeting.meeting_id

        url_args["fullName"] = self.full_name

        if self.user_id:
            url_args["userID"] = self.user_id

        if self.role == Role.MODERATOR and self.meeting.moderator_pw:
            url_args["password"] = self.meeting.moderator_pw
        elif self.role == Role.VIEWER and self.meeting.attendee_pw:
            url_args["password"] = self.meeting.attendee_pw
        else:
            raise ValueError(f"Unknown role {self.role} or unavailable password")

        url_args["createTime"] = str(self.meeting.create_time)

        if browser or not do_join:
            url_args["redirect"] = "true"
            url = self.meeting.api._build_url("join", url_args)

            if browser:
                logger.info("Handing join request off to default browser")
                webbrowser.open(url)

            return url
        elif do_join:
            url_args["redirect"] = "false"

            logger.debug("Sending join request")
            res = self.meeting.api._request("join", url_args)
            self._update_from_response(res)

            return self.url

    def _update_from_response(self, res: Dict[str, Any]) -> None:
        for name, value in res.items():
            if name == "role":
                self.role = Role(value)
            else:
                snake_name = camel_to_snake(name)

                if hasattr(self, snake_name):
                    setattr(self, snake_name, to_field_type(self, snake_name, value))

    def to_dict(self, *args: str, **kwargs: str) -> Dict[str, Any]:
        """Return relevant data of this attendee as a dictionary.

        The dictionary can be used to build an XML document compatible
        with BigBlueButton API clients.

        If names of attributes are passed as positional arguments, only
        these attributes are returned in the dictionary.

        If attribute names are passed as names of keyword arguments,
        they are renamed to the string passed as value in the dictionary.
        """
        res: Dict[str, Any] = {}

        for name, value in self.__dict__.items():
            if args and name not in args and name not in kwargs:
                continue

            if name == "meeting":
                res["meetingID"] = self.meeting.meeting_id
            elif value is not None:
                if name in kwargs:
                    camel_name = kwargs[name]
                else:
                    camel_name = snake_to_camel(name)

                if isinstance(value, bool):
                    str_value = "true" if value else "false"
                else:
                    str_value = str(value)

                res[camel_name] = str_value

        return res

    @classmethod
    def get_kwargs_from_url_args(
        cls, urlargs: Dict[str, str], meeting: "Meeting"
    ) -> Dict[str, Any]:
        """Construct a dictionary suitable for passing as kwargs to the constructor.

        The passed urlargs are expected to be a dictionary of URL arguments following
        the BigBlueButton HTTP API schema.

        This is useful to generate an attendee object from a URL call from a foreign
        BBB client, an API reply, or comparable things.
        """
        kwargs: Dict[str, Any] = {}

        for name, value in urlargs.items():
            if name == "password":
                # Determine role by used password
                if value == meeting.attendee_pw:
                    kwargs["role"] = Role.VIEWER
                elif value == meeting.moderator_pw:
                    kwargs["role"] = Role.MODERATOR
                else:
                    raise ValueError("Invalid password passed, could not determine role")
            elif name == "meetingID":
                if value != meeting.meeting_id:
                    raise ValueError("Meeting ID does not match")
            elif name == "createTime":
                if int(value) != meeting.create_time:
                    raise ValueError("createTime does not match actual meeting parameters")
            else:
                snake_name = camel_to_snake(name)
                kwargs[snake_name] = to_field_type(cls, snake_name, value)

        return kwargs
