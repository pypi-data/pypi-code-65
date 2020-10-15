import attr

from tdxapi.managers.bases import TdxManager
from tdxapi.managers.impact import ImpactManager
from tdxapi.managers.mixins import TdxAppMixin
from tdxapi.managers.priority import PriorityManager
from tdxapi.managers.ticket_source import TicketSourceManager
from tdxapi.managers.ticket_type import TicketTypeManager
from tdxapi.managers.urgency import UrgencyManager


@attr.s
class TicketApplication(TdxManager, TdxAppMixin):
    def __attrs_post_init__(self):
        self.impacts = ImpactManager(self.dispatcher, self.app_id)
        self.priorities = PriorityManager(self.dispatcher, self.app_id)
        self.sources = TicketSourceManager(self.dispatcher, self.app_id)
        self.types = TicketTypeManager(self.dispatcher, self.app_id)
        self.urgencies = UrgencyManager(self.dispatcher, self.app_id)
