import logging
import typing
from typing import Dict, Text

import convo.shared.utils.common
from convo.shared.utils.cli import print_warning
from convo.shared.constants import DOCS_BASE_URL
from convo.core.lock_store import LockStore

logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from convo.core.agent import Agent


def run(
    model: Text,
    endpoints: Text,
    connector: Text = None,
    credentials: Text = None,
    **kwargs: Dict,
):
    """Runs a Convo model.

    Args:
        model: Path to model archive.
        endpoints: Path to endpoints file.
        connector: Connector which should be use (overwrites `credentials`
        field).
        credentials: Path to channel credentials file.
        **kwargs: Additional arguments which are passed to
        `convo.core.run.serve_application`.

    """
    import convo.core.run
    import convo.nlu.run
    from convo.core.utils import AvailableEndpoints
    import convo.utils.common as utils

    _endpoints = AvailableEndpoints.read_endpoints(endpoints)

    if not connector and not credentials:
        connector = "rest"
        print_warning(
            f"No chat connector configured, falling back to the "
            f"REST input channel. To connect your bot to another channel, "
            f"read the docs here: {DOCS_BASE_URL}/messaging-and-voice-channels"
        )

    kwargs = convo.shared.utils.common.minimal_kwargs(
        kwargs, convo.core.run.serve_application
    )
    convo.core.run.serve_application(
        model,
        channel=connector,
        credentials=credentials,
        endpoints=_endpoints,
        **kwargs,
    )


def create_agent(model: Text, endpoints: Text = None) -> "Agent":
    from convo.core.tracker_store import TrackerStore
    from convo.core.utils import AvailableEndpoints
    from convo.core.agent import Agent
    from convo.core.brokers.broker import EventBroker

    _endpoints = AvailableEndpoints.read_endpoints(endpoints)

    _broker = EventBroker.create(_endpoints.event_broker)
    _tracker_store = TrackerStore.create(_endpoints.tracker_store, event_broker=_broker)
    _lock_store = LockStore.create(_endpoints.lock_store)

    return Agent.load(
        model,
        generator=_endpoints.nlg,
        tracker_store=_tracker_store,
        lock_store=_lock_store,
        action_endpoint=_endpoints.action,
    )
