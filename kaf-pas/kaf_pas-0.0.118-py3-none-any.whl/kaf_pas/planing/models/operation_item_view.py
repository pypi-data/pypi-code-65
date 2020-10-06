import logging

from django.db.models import DecimalField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.managers.common_manager import CommonManager
from isc_common.models.audit import AuditModel
from isc_common.number import DecimalToStr
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.planing.models.levels import Levels
from kaf_pas.planing.models.operation_refs import Operation_refsManager
from kaf_pas.planing.models.operation_types import Operation_types
from kaf_pas.planing.models.operations import BaseOperationQuerySet
from kaf_pas.production.models.launches import Launches
from kaf_pas.production.models.resource import Resource

logger = logging.getLogger(__name__)


class Operation_item_viewQuerySet(BaseOperationQuerySet):
    pass


class Operation_item_viewManager(CommonManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
            'value1_sum': DecimalToStr(record.value1_sum),
            'value_sum': DecimalToStr(record.value_sum),
            'relevant': record.item.relevant,
            'STMP_1__value_str': record.item.STMP_1.value_str if record.item.STMP_1 else None,
            'STMP_1_id': record.item.STMP_1.id if record.item.STMP_1 else None,
            'STMP_2__value_str': record.item.STMP_2.value_str if record.item.STMP_2 else None,
            'STMP_2_id': record.item.STMP_2.id if record.item.STMP_2 else None,
            'version': record.item.version,
            'where_from': record.item.where_from,
        }
        return res

    def get_queryset(self):
        return Operation_item_viewQuerySet(self.model, using=self._db)


class Operation_item_view(AuditModel):
    launch = ForeignKeyProtect(Launches)
    level = ForeignKeyProtect(Levels)
    resource = ForeignKeyProtect(Resource)
    location = ForeignKeyProtect(Locations)
    opertype = ForeignKeyProtect(Operation_types)
    item = ForeignKeyProtect(Item)
    value_sum = DecimalField(decimal_places=4, max_digits=19)
    value1_sum = DecimalField(decimal_places=4, max_digits=19)
    props = Operation_refsManager.props()

    objects = Operation_item_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        managed = False
        db_table = 'planing_operation_item_view'
        verbose_name = 'Ресурсы операций'
