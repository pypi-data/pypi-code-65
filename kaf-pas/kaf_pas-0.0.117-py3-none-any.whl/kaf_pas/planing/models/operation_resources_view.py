import logging

from django.conf import settings

from isc_common import setAttr
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_manager import CommonQuerySet, CommonManager
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.planing.models.levels import Levels
from kaf_pas.planing.models.operation_item_view import Operation_item_view
from kaf_pas.planing.models.operation_refs import Operation_refsManager
from kaf_pas.planing.models.operation_types import Operation_types
from kaf_pas.production.models.launches import Launches
from kaf_pas.production.models.resource import Resource

logger = logging.getLogger(__name__)


class Operation_resources_viewQuerySet(CommonQuerySet):
    def get_range_rows1(self, request, function=None, distinct_field_names=None, remove_fields=None):
        request = DSRequest(request=request)
        data = request.get_data()
        launch_id = data.get('launch_id')
        if launch_id:
            launch = Launches.objects.get(id=launch_id)
            if launch.parent is not None:
                items = [operation_item_view.item for operation_item_view in Operation_item_view.objects.filter(opertype_id=settings.OPERS_TYPES_STACK.ROUTING_TASK.id, launch=launch).distinct()]
                setAttr(request.json.get('data'), 'launch_id', launch.parent.id)
                setAttr(request.json.get('data'), 'item', items)

        self.alive_only = request.alive_only
        self.enabledAll = request.enabledAll
        res = self.get_range_rows(start=request.startRow, end=request.endRow, function=function, distinct_field_names=distinct_field_names, json=request.json, criteria=request.get_criteria())
        return res


class Operation_resources_viewManager(CommonManager):

    @staticmethod
    def getRecordLocations(record):
        return dict(id=record.location.id, title=record.location.name, prompt=record.location.full_name)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'full_name': record.full_name,
            'description': record.description,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Operation_resources_viewQuerySet(self.model, using=self._db)


class Operation_resources_view(AuditModel):
    launch = ForeignKeyProtect(Launches)
    level = ForeignKeyProtect(Levels)
    item = ForeignKeyProtect(Item)
    resource = ForeignKeyProtect(Resource)
    location = ForeignKeyProtect(Locations)
    opertype = ForeignKeyProtect(Operation_types)
    executor = ForeignKeyProtect(User, null=True, blank=True)
    props = Operation_refsManager.props()

    objects = Operation_resources_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        managed = False
        db_table = 'planing_operation_resources_view'
        verbose_name = 'Ресерсы операций'
