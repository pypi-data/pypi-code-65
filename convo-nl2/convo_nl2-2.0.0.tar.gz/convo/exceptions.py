from typing import Text

from convo.shared.exceptions import ConvoException


class ModelNotFound(ConvoException):
    """Raised when a model is not found in the path provided by the user."""


class NoEventsToMigrateError(ConvoException):
    """Raised when no events to be migrated are found."""


class NoConversationsInTrackerStoreError(ConvoException):
    """Raised when a tracker store does not contain any conversations."""


class NoEventsInTimeRangeError(ConvoException):
    """Raised when a tracker store does not contain events within a given time range."""


class MissingDependencyException(ConvoException):
    """Raised if a python package dependency is needed, but not installed."""


class PublishingError(ConvoException):
    """Raised when publishing of an event fails.

    Attributes:
        timestamp -- Unix timestamp of the event during which publishing fails.
    """

    def __init__(self, timestamp: float) -> None:
        self.timestamp = timestamp
        super(PublishingError, self).__init__()

    def __str__(self) -> Text:
        return str(self.timestamp)
