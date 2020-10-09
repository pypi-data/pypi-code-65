"""Data structures to handle BigBlueButton servers.

This module also contains group handling support and the implementation
of the communication with the API itself. Meetings and attendees manage
themselves by talking to the :class:`BigBlueButton` object linked to them. All
other methods should be called on a :class:`BigBlueButtonGroup`, which takes care
of routing to the appropriate server(s).
"""

import concurrent.futures
import json
import logging
import random
import subprocess  # noqa: S404
from dataclasses import dataclass, field
from hashlib import sha1
from socket import getfqdn
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union
from urllib.parse import urlencode
from uuid import uuid1

import requests
import xmltodict

from ._caching import cache
from .attendee import Attendee
from .loadbalancing import CHECKERS as lb_checkers
from .meeting import Meeting

try:
    from sadf import SadfCommand, SadfReport
    import sadf.fieldgroups as sadf_fieldgroups
except ImportError:  # pragma: no cover
    SadfCommand, SadfReport, sadf_fieldgroups = None, None, None


logger = logging.getLogger(__name__)


class BigBlueButtonError(Exception):
    """Exception raised when a BigBlueButton backends encounters an error."""
    pass


@dataclass
class BigBlueButton:
    """One BigBlueButton server.

    A BigBlueButton instance holds the information needed to communicate with the
    BigBlueButton server. When creating meetings, it passes itself to the
    :class:`~bigbluebutton.api.meeting.Meeting` object, and provides methods for
    the Meeting object to manage itself.

    A BigBlueButton server always belongs to a :class:`BigBlueButtonGroup`, which it gets
    passed in the constructor and it registers itself with.

    :param group: Reference to the :class:`BigBlueButtonGroup` this server belongs to
    :param name: Descriptive name of this server
    :param url: Full URL to the API endpoint of this BigBlueButton server (with trailing /)
    :param salt: API secret, as reported by bbb-conf on the server
    :param host: Hostname of the server, e.g. for SSH access (guessed from URL if unset)
    :param request_timeout: Timeout for API requests, either one value or a two-tuple
                            defining TCP and HTTP request timeouts
    """

    group: "BigBlueButtonGroup"
    name: str

    url: str
    salt: str
    host: Optional[str] = field(default=None, compare=False)

    meetings: Dict[str, "Meeting"] = field(default_factory=dict, init=False, compare=False)
    sysstat: Optional[SadfReport] = field(default=None, init=False, compare=False)

    request_timeout: Union[float, Tuple[float, float]] = field(default=(0.5, 10), compare=False)
    cache_timeout: float = field(default=30, compare=False)

    def __post_init__(self):
        """Set up the server object to work properly.

        1. Self-register with the :class:`BigBlueButtonGroup` passed.
        2. Set-up HTTP session store (for cookies, etc.).
        """
        self.group.apis[self.name] = self
        logger.debug(f"Self-registered server {self.name} in group {self.group.name}")

        # Use persistent HTTP session to track JSESSIONID cookie (et al)
        self._session = cache.get(f"{self.url}::session") or requests.Session()

        # Restore meeting and sysstat data from last time if any
        self.meetings = cache.get(f"{self.url}::meetings") or {}
        self.sysstat = cache.get(f"{self.url}::sysstat")

    def __del__(self):
        """Store some data for next time."""
        cache.set(f"{self.url}::meetings", self.meetings, self.cache_timeout)
        cache.set(f"{self.url}::session", self._session, self.cache_timeout)
        cache.set(f"{self.url}::sysstat", self.sysstat, self.cache_timeout)

    @staticmethod
    def request_checksum(call: str, query: str, salt: str) -> str:
        """Compute the checksum needed to authenticate API requests to a BigBlueButton server.

        The checksum has to be sent with every API request and is constructed like this:

          1. Build the full query string (already done when passed into this method)
          2. Prepend the name of the API call, without delimiter
          3. Append the API salt (shared secret, key,…) provided by the BBB server
          4. Calculate the SHA1 sum of the resulting string

        >>> BigBlueButton.request_checksum("isMeetingRunning", "meetingID=Foo", "MyTestSalt")
        'f59b73c5cf1db387da4ca7d937049420d4c50a12'

        The resulting checksum is added tothe original query string as a parameter called
        checksum.

        :param call: Name of the API method to call (last part of URL)
        :param query: urlencoded query string with call parameters
        :param salt: The API secret the server expects requests to be signed with

        :return: The checksum (to be appended as the checksum parameter)
        """
        hash_string = call + query + salt
        checksum = sha1(hash_string.encode()).hexdigest()  # noqa: S303, we have no choice

        return checksum

    def _build_url(self, call: str, params: Optional[Dict[str, str]] = None) -> str:
        # Generate query string with challenge-response checksum
        # cf. https://docs.bigbluebutton.org/dev/api.html#usage
        query = urlencode(params or {})
        query += "&checksum=" + self.request_checksum(call, query, self.salt)

        url = f"{self.url}{call}?{query}"
        return url

    def _request(self, call: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = self._build_url(call, params)

        res = self._session.get(url, timeout=self.request_timeout)
        if res.status_code != 200:
            raise BigBlueButtonError(f"Backend returned HTTP status {res.status_code}.")

        try:
            xml = xmltodict.parse(res.text)
        except Exception as ex:
            raise BigBlueButtonError("Failed to parse XML response from backend.") from ex

        if xml.get("returncode", "FAILED").upper() == "FAILED":
            message_key = res.get("messageKey", "")
            message = res.get("message", "Unknown error")

            ex = BigBlueButtonError(f"Backend returned FAILED response: {message}")
            ex.message_key = message_key
            raise ex

        return xml["response"]

    def create_meeting(self, do_create: bool = True, *args, **kwargs) -> Meeting:
        """Create a meeting on thie BigBlueButton server.

        args and kwargs are passed verbatim into the
        :class:`~bigbluebutton.api.meeting.Meeting` constructor. The additional parameter
        do_create determines whether the API is actually called to create the meeting. If
        it is False, tje object is returned but the meeting is not transferred to the
        BigBlueButton server.

        This method first looks up whether a meeting with the passed meeting_id
        and reuse that object if a meeting is found. If none is found, a new object
        is created and the create API call sent to the server (if do_create is not
        set to False).

        The BigBlueButton API guarantees that the create call is idempotent,
        so calling this method on a meeting ID of an existing meeting is safe. But,
        as every server is part of a server group, consumers should always call
        create_meeting on a :class:`BigBlueButtonGroup` instead (or use its meeting property
        to make use of caching).

        :param do_create: True to call the create API method on the server, False to only
                          create the Meeting object

        :return: The found or newly created Meeting object
        """
        if "meeting_id" in kwargs and kwargs["meeting_id"] in self.meetings:
            meeting = self.meetings[kwargs["meeting_id"]]
        else:
            meeting = Meeting(self, *args, **kwargs)

        if do_create:
            meeting.create()
        else:
            meeting.get_meeting_info()

        return meeting

    def get_meetings(self, filter_meta: Optional[Dict[str, str]] = None) -> Dict[str, "Meeting"]:
        """Get all meetings known on the BigBlueButton server.

        This method calls the getMeetings API call on the BigBlueButton server
        and constructs Meeting objects from all meetings in the result. For meetings
        that are already known as objects, the appropriate object is returned; for
        all unknown meetings, new objects are created.

        As every server is part of a server group, consumers should always call
        :func:`BigBlueButtonGroup.create_meeting` instead.

        The results are returned after filtering on the `filter_meta` argument;
        see :meth:`filter_meetings` for details.

        :return: A dictionary mapping meeting IDs to Meeting objects
        """
        logger.info(f"Updating meetings on server {self.name}")
        res = self._request("getMeetings")

        found_meeting_ids = []

        if "meetings" not in res or not res["meetings"] or not res["meetings"]["meeting"]:
            self.meetings.clear()
            logger.info(f"Cleared all meetings from server {self.name}")
        else:
            if not isinstance(res["meetings"]["meeting"], list):
                res["meetings"]["meeting"] = [res["meetings"]["meeting"]]

            for meeting_dict in res["meetings"]["meeting"]:
                meeting_id = meeting_dict["meetingID"]

                if meeting_id in self.meetings:
                    meeting = self.meetings[meeting_id]
                    logger.debug(f"Meeting {meeting_id} already known on server {self.name}")
                else:
                    meeting = Meeting(self, meeting_id=meeting_id)
                    self.meetings[meeting_id] = meeting
                    logger.debug(f"Meeting {meeting_id} discovered, adding to server {self.name}")

                meeting._update_from_response(meeting_dict)

                # Track found IDs for later clean up
                found_meeting_ids.append(meeting_id)

        # Clean up meetings not known anymore
        for meeting_id in list(self.meetings.keys()):
            if meeting_id not in found_meeting_ids:
                del self.meetings[meeting_id]

        return BigBlueButton.filter_meetings(self.meetings, filter_meta)

    @staticmethod
    def filter_meetings(
        meetings: Dict[str, "Meeting"], filter_meta: Optional[Dict[str, str]] = None
    ) -> Dict[str, "Meeting"]:
        """Filter the known meetings on meta-data.

        See :meth:`Meeting.matches_meta` for the semantics of the arguments.
        """
        return dict(filter(lambda i: i[1].matches_meta(filter_meta), meetings.items()))

    def ssh_command(
        self, command: Sequence[str], input_: Optional[str] = None
    ) -> subprocess.CompletedProcess:
        """Execute a shell command through an SSH connection to the server.

        This method constructs an ssh command and runs it as a subprocess,
        without shell expansion. However, shell expansion WILL take place
        on the server side.

        The subprocess result is returned verbatim.

        :param command: Sequence of command words, like in argv
        :param input_: Text to pipe into the command on stdin
        :return: The verbatim subprocess object (including stdout, stderr,
                 and return code)
        """
        if self.host is None:
            raise ValueError(f"Server {self.name} has no hostname set")
        args: List[str] = ["ssh", self.host] + list(command)

        logger.info(f"Running SSH command {args} on {self.name}")
        res = subprocess.run(  # noqa: S603, command injection is intended
            args, capture_output=True, input=input_, text=True
        )
        return res

    def get_sysstat(self) -> Optional[SadfReport]:
        """Get the output of the sadf/sar command (from the sysstat package) through SSH.

        The result is used when load-balancing API requests.

        To use this functaionality, the sadf Python package (in the "sysstat" extra)
        must be installed.
        """
        if SadfCommand is None:
            logger.warn(f"sysstat requested on host {self.name}, but python-sadf unavailable")
            self.sysstat = None
            return None

        logger.info(f"Getting system statistics on server {self.name}")

        # Let the python-sadf library build a command, but do not run it
        sadf_cmd = SadfCommand()
        sadf_cmd.field_groups = [
            sadf_fieldgroups.CPULoad(all_fields=True),
            sadf_fieldgroups.IO(),
            sadf_fieldgroups.Kernel(),
            sadf_fieldgroups.Memory(all_fields=True),
            sadf_fieldgroups.Network(dev=True, edev=True, sock=True),
            sadf_fieldgroups.Queue(),
        ]
        cmd = sadf_cmd._build_command()
        # Prepend environment python-sadf woud use
        cmd = ["env"] + [f"{k}={v}" for k, v in sadf_cmd._command_env.items()] + cmd

        # Execute using our own runner and extract data
        ret = self.ssh_command(cmd)
        if ret.returncode == 0:
            try:
                host_data = json.loads(ret.stdout)["sysstat"]["hosts"][0]
            except (KeyError, json.JSONDecodeError):
                logger.error(f"sadf produced invalid data on host {self.name}")
            else:
                # Hand back to python-sadf to generate pandas report
                self.sysstat = SadfReport(host_data, sadf_cmd.field_groups)
        else:
            logger.warn(f"sadf unavailable or failing on host {self.name}")

        return self.sysstat

    def refresh(self) -> None:
        """Refresh various aspects of this server.

        - Meetings
        - Sysstat data
        """
        logger.debug(f"Fully refreshing server {self.name}")
        self.get_meetings()
        self.get_sysstat()


@dataclass
class BigBlueButtonGroup:
    """A set of BigBlueButton servers.

    All API operations should be called on this object, instead of
    a single server. It takes care of aggregating results from the
    backend servers (e.g. for getMeetings) and of routing requests
    to the correct server (e.g. for loadbalancing on create).

    Servers (:class:`BigBlueButton` objects) register themselves to the group
    passed as first argument on instantiation.

    If only one server has to be handled, still place it in a group.

    :param name: Descriptive name of this server group
    :param workers: Number of servers to operate on parallely, e.g. when
                    retrieving meetings or running SSH commands)
    :param logout_url: Default URL to redirect clients to on meeting end
    :param origin: Name of the origin software passed as meeting meta-data
    :param origin_server_name: Hostname of the origin, passed as meeting meta-data;
                               defaults to the systems's local FQDN
    :param generate_meeting_id_cb: Callable to run for generating meeting IDs
    """

    name: str

    apis: Dict[str, BigBlueButton] = field(default_factory=dict, init=False, compare=False)
    workers: int = field(default=10, compare=False)

    logout_url: Optional[str] = field(default=None, compare=False)
    origin: str = "python-bigbluebutton2"
    origin_server_name: str = field(default_factory=getfqdn)

    generate_meeting_id_cb: Optional[Callable[[], str]] = field(default=None, compare=False)

    def generate_meeting_id(self) -> str:
        """Generate a unique meeting ID.

        By default, this returns a GUID, unless a callback was defined in the
        `generate_meeting_id_cb` attribute.
        """
        if self.generate_meeting_id_cb is None:
            return str(uuid1())
        else:
            return self.generate_meeting_id_cb()

    @property
    def meetings(self) -> Dict[str, "Meeting"]:
        """All meetings known on all servers in the group.

        Each meeting will reference the backend server it is actually
        running on, so calling methods on the Meeting objects returned
        in this property always does "the right thing".
        """
        res = {}

        for name, api in self.apis.items():
            res.update(api.meetings)

        return res

    def new(self, name: str, *args, **kwargs) -> BigBlueButton:
        """Createa new :class:`BigBlueButton` server object in this group.

        The server object will register itself in this group.

        For the arguments, see the documentation of
        :class:`BigBlueButton`.
        """
        logger.debug(f"Creating new API client {name}")
        bbb = BigBlueButton(self, name, *args, **kwargs)
        return bbb

    def _foreach(self, method: str, *args, **kwargs) -> Dict[str, Any]:
        logger.debug(
            f"Calling method {method} on all servers in group {self.name} ({self.workers} workers)"
        )
        res = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {}
            for name, bbb in self.apis.items():
                fn = getattr(bbb, method)
                futures[pool.submit(fn, *args, **kwargs)] = name
                logger.debug(f"Pooled method {method} on server {name}")

            logger.debug("Waiting for pooled methods")
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                res[name] = future.result()
                logger.debug(f"Pooled method {method} on server {name} returned")

        return res

    def get_meetings(self, filter_meta: Optional[Dict[str, str]] = None) -> Dict[str, "Meeting"]:
        """Update meeting information on all server objects.

        It is aggregated into the meetings attribute.

        If forcefully updating the metting information cache is not intended,
        the meeting property should be used instead.
        """
        self._foreach("get_meetings")
        return BigBlueButton.filter_meetings(self.meetings, filter_meta)

    def ssh_command(
        self, command: Sequence[str], input_: Optional[str] = None
    ) -> Dict[str, subprocess.CompletedProcess]:
        """Call an SSH command on each backend server in this group.

        For the arguments and behaviour, see the documentation of
        :func:`BigBlueButton.ssh_command`.

        The return value is a dictionary with the server name as key
        and the result of the server's ssh_command method as value.
        """
        res = self._foreach("ssh_command", command, input_)
        return res

    def get_sysstat(self) -> Dict[str, Optional[SadfReport]]:
        """Get sysstat information from all backend servers.

        For the arguments and behaviour, see the documentation of
        :func:`BigBlueButton.get_sysstat`.

        The result is a dictionary with the server name as key and
        the result of the server's get_sysstat method as values.
        """
        res = self._foreach("get_sysstat")
        return res

    def refresh(self) -> None:
        """Refresh all backend servers.

        For a description of the behaviour, see the documentation of
        :func:`BigBlueButton.refresh`.
        """
        self._foreach("refresh")

    def select_api(self, criteria: Optional[Dict[str, Any]] = None) -> BigBlueButton:
        """Select a target server in the group by some creiteria.

        This method runs a ranking algorithm on all servers in the group, then
        returns the server with the highest ranking. This can be used for
        load-balancing and similar tasks.

        The ranking algorithm works like this:

        1. Start with giving each server a ranking of N points.
        2. Apply a list of checkers on each server. Each checker returns a factor
           by which to multiply the last known ranking (between 0 and 1).
        3. Return the server with the highest ranking. If multiple servers share the
           same highest ranking, fall back to round robin.

        A ranking of 0 means a server is unavailable. Servers with a ranking of 0 are
        never returned.

        :param criteria: A dictionary of criteria taken into account by each checker.
                         See the documentation of the checkers in the
                         :module:`bigbluebutton.api.loadbalancing` module for details
                         on what criteria exist and how they influence server selection.
        :return: One BigBlueButton server that best matches the criteria
        """
        # Start with a ranking of 10 for each API
        apis = {api_name: 10.0 for api_name in self.apis}

        # Define checkers to run on each API
        # Each checker returns a factor to scale the ranking by
        checkers = lb_checkers

        # Apply checkers, in order
        for checker in checkers:
            for api_name, ranking in apis.items():
                factor = checker(self.apis[api_name], criteria)
                apis[api_name] *= factor

        # Get maximum ranking and all APIs that got it
        max_ranking = max(apis.values())
        apis_won = [
            self.apis[api_name] for api_name, ranking in apis.items() if ranking == max_ranking
        ]

        # Select random API from winners
        api = random.choice(apis_won)  # noqa: S311, not cryptographic
        return api

    def create_meeting(
        self, do_create: bool = True, filter_meta: Optional[Dict[str, str]] = None, *args, **kwargs
    ) -> Meeting:
        """Create a new meeting on one of the backend servers.

        For the arguments, see the documentation on :class:`~bigbluebutton.api.meeting.Meeting`.

        This method first tries to find an existing meeting. The original
        create API method in BigBlueButton is idempotent, so we must ensure
        we also fulfill this requirement when handling several servers. If this
        group already has a list of known meetings, and the meeting is found in it,
        the call is redirected to the backend server it is linked to. If it is not
        found, :func:`get_meetings` is called to refresh the cache to be certain.

        If all attempts to find a meeting with the ID fail, or no ID is passed,
        a backend server is selected using :func:`select_api` and the create call
        routed there.
        """
        if "meeting_id" in kwargs:
            meeting = self._find_meeting(kwargs["meeting_id"])
            if meeting and not self._find_meeting(kwargs["meeting_id"], filter_meta):
                logger.info(
                    f"Found meeting with id {meeting.meeting_id} on server {api.name}, but meta-data did not match"
                )
                logger.warn(
                    f"Stripping meeting id {meeting.meeting_id} from create request due to collision"
                )
                meeting = None
                del kwargs["meeting_id"]
        else:
            meeting = None

        if meeting:
            api = meeting.api
            logger.info(f"Found meeting with id {meeting.meeting_id} on server {api.name}")
        else:
            logger.info(f"Creating new meeting on one server in group {self.name}")
            api = self.select_api()

        return api.create_meeting(do_create, *args, **kwargs)

    def _find_meeting(
        self, meeting_id: str, filter_meta: Optional[Dict[str, str]] = None
    ) -> Optional[Meeting]:
        if (
            meeting_id in self.meetings or meeting_id in self.get_meetings()
        ) and meeting_id in BigBlueButton.filter_meetings(self.meetings, filter_meta):
            return self.meetings[meeting_id]
        return None

    def is_meeting_running(
        self, meeting_id: str, filter_meta: Optional[Dict[str, str]] = None
    ) -> bool:
        """Determine whether a meeting with a given ID is running on any backend server."""
        meeting = self._find_meeting(meeting_id, filter_meta)
        if meeting:
            return meeting.is_meeting_running()
        else:
            return False

    def end_meeting(
        self,
        meeting_id: str,
        password: Optional[str] = None,
        filter_meta: Optional[Dict[str, str]] = None,
    ) -> None:
        """End a meeting determined from the passed ID.

        If the meeting is not found, this method silently does nothing.

        If a password is passed as second argument, it is compared against
        the moderarotr password of the meeting before the end request is even
        sent to the backend.
        """
        meeting = self._find_meeting(meeting_id, filter_meta)
        if meeting:
            # Verify password before even sending the call, if provided
            # Entirely useless because anyone who can call end can also call getMeetingInfo,
            # but let's play along…
            if password is not None and password != meeting.moderator_pw:
                raise ValueError("The supplied moderatorpassword does not match.")
            meeting.end()

    def handle_from_data(
        self,
        method: str,
        attrs: Optional[dict] = None,
        content: Optional[str] = None,
        filter_meta: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Handle an API call from a method, a dict of parameters, and a text body.

        This method is useful to pass on structures like HTTP requests on to the
        library, e.g. when writing a proxy or load balancer. The method name and
        parameter dictionary are expected to match the official BigBlueButton API.

        The return value is a dictionary representation of the XML document as would
        be returned by a BigBlueButton server when called with the same parameters.
        """
        if not attrs:
            attrs = {}

        meeting: Optional["Meeting"]
        if method == "create":
            kwargs = Meeting.get_kwargs_from_url_args(attrs)
            # Merge filter_meta into created meeting, so later responses can be filtered on it
            kwargs.setdefault("meta", {}).update(filter_meta or {})

            meeting = self.create_meeting(**kwargs)

            return meeting.to_dict()
        elif method == "join":
            meeting = self._find_meeting(attrs["meetingID"], filter_meta)
            if meeting:
                kwargs = Attendee.get_kwargs_from_url_args(attrs, meeting)
                attendee = Attendee(meeting=meeting, **kwargs)
                attendee.join()

                # We need to construct this one response manually, because for some inobvious
                # reason the designers of the BBB API changed their minds and started using
                # snake_case instead of dromedarCase
                return {
                    "meeting_id": meeting.meeting_id,
                    "user_id": attendee.user_id,
                    "auth_token": attendee.auth_token,
                    "session_token": attendee.session_token,
                    "url": attendee.url,
                }
            else:
                raise KeyError("Meeting not found.")
        elif method == "isMeetingRunning":
            running = self.is_meeting_running(attrs["meetingID"], filter_meta)
            return {"running": "true" if running else "false"}
        elif method == "end":
            self.end_meeting(attrs["meetingID"], attrs["password"], filter_meta)
            return {}
        elif method == "getMeetingInfo":
            meeting = self._find_meeting(attrs["meetingID"], filter_meta)
            if meeting:
                meeting.get_meeting_info()
                return meeting.to_dict()
            else:
                raise KeyError("Meeting not found.")
        elif method == "getMeetings":
            meetings = self.get_meetings(filter_meta)
            return {
                "meetings": [
                    {"meeting": meeting.to_dict()} for meeting_id, meeting in meetings.items()
                ]
            }
        elif method == "getRecordings":
            raise NotImplementedError(f"Method {method} not implemented yet")
        elif method == "publishRecordings":
            raise NotImplementedError(f"Method {method} not implemented yet")
        elif method == "deleteRecordings":
            raise NotImplementedError(f"Method {method} not implemented yet")
        elif method == "updateRecordings":
            raise NotImplementedError(f"Method {method} not implemented yet")
        elif method == "getDefaultConfigXML":
            raise NotImplementedError(f"Method {method} not implemented yet")
        elif method == "setConfigXML":
            raise NotImplementedError(f"Method {method} not implemented yet")
        elif method == "getRecordingTextTracks":
            raise NotImplementedError(f"Method {method} not implemented yet")
        elif method == "putRecordingTextTrack":
            raise NotImplementedError(f"Method {method} not implemented yet")
        else:
            raise TypeError(f"Method {method} is unknown")
