from convo.constants import DOCS_URL_EVENT_BROKERS
from convo.core.brokers.file import FileEventBroker
from convo.utils.common import raise_warning


class FileProducer(FileEventBroker):
    raise_warning(
        "The `FileProducer` class is deprecated, please inherit from "
        "`FileEventBroker` instead. `FileProducer` will be removed in "
        "future Convo versions.",
        FutureWarning,
        docs=DOCS_URL_EVENT_BROKERS,
    )
