from convo.core.brokers.broker import EventBroker


# noinspection PyAbstractClass
from convo.utils.common import raise_warning


class EventChannel(EventBroker):
    raise_warning(
        "The `EventChannel` class is deprecated, please inherit from "
        "`EventBroker` instead. `EventChannel` will be removed "
        "in future Convo versions.",
        DeprecationWarning,
        stacklevel=2,
    )
