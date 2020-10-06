from enum import Enum
from typing import List, Optional

from enstadtpfaff_platform_mock_api.event import Event
from enstadtpfaff_platform_mock_api.util.topic_util import name_for_shared_topic


class Category(Enum):
    NATURE = 'NATURE'
    HOUSEHOLD = 'HOUSEHOLD'
    MOBILITY = 'MOBILITY'
    ENERGY = 'ENERGY'
    FAMILY = 'FAMILY'
    GROCERIES = 'GROCERIES'
    FREETIME = 'FREETIME'
    HEATING = 'HEATING'
    MISC = 'MISC'


# noinspection PyPep8Naming
class Hint:
    def __init__(
            self,
            headline: str,
            content: str,
            categories: List[Category],
            recipients: Optional[List[str]] = None,
            issuedBy: Optional[str] = None,
            issuedAt: Optional[str] = None,
            basedOn: Optional[List[str]] = None,
            validityBegin: Optional[str] = None,
            validityEnd: Optional[str] = None
    ):
        self.headline = headline
        self.content = content
        self.categories = list(
            map((lambda category: category if isinstance(category, str) else category.value), categories)
        )
        self.recipients = recipients
        self.issuedBy = issuedBy
        self.issuedAt = issuedAt
        self.basedOn = basedOn
        self.validityBegin = validityBegin
        self.validityEnd = validityEnd


class HintsEventBuilder:
    SHARED_TOPIC_ID = "hints"
    HINTS_TOPIC = name_for_shared_topic(
        SHARED_TOPIC_ID
    )

    @staticmethod
    def hint(
            hint: Hint
    ) -> Event:
        payload = HintsEventBuilder._del_none(vars(hint))
        return Event(
            HintsEventBuilder.HINTS_TOPIC,
            payload
        )

    @staticmethod
    def _del_none(d):
        """
        Delete keys with the value ``None`` in a dictionary, recursively.
        """
        if not isinstance(d, dict):
            return d
        return dict((k, HintsEventBuilder._del_none(v)) for k, v in d.items() if v is not None)
