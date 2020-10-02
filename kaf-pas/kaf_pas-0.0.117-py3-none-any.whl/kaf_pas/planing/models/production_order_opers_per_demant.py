import logging

from django.db.models import DecimalField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.managers.common_manager import CommonManager, CommonQuerySet
from isc_common.models.audit import AuditModel
from isc_common.models.standard_colors import Standard_colors
from isc_common.number import DecimalToStr
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.item import Item
from kaf_pas.production.models.launches import Launches
from kaf_pas.sales.models.demand import Demand

logger = logging.getLogger(__name__)


class Production_order_opers_per_demandManagerQuerySet(CommonQuerySet):
    pass


class Production_order_opers_per_demandManager(CommonManager):
    @staticmethod
    def getRecord(record):
        res = {
            'edizm__code': record.edizm.code,
            'edizm__name': record.edizm.name,
            'edizm_id': record.edizm.id,
            'color__color': record.color.color if record.color else None,
            'color__name': record.color.name if record.color else None,
            'color_id': record.color.id if record.color else None,
            'demand_id': record.demand.id if record.demand else None,
            'demand__date': record.demand.date if record.demand else None,
            'demand__code': record.demand.code if record.demand else None,
            'launch_id': record.launch.id,
            'launch__date': record.launch.date,
            'launch__code': record.launch.code,
            'id': record.id,
            'value_made': DecimalToStr(record.value_made),
        }
        return res

    def get_queryset(self):
        return Production_order_opers_per_demandManagerQuerySet(self.model, using=self._db)


class Production_order_opers_per_demand(AuditModel):
    demand = ForeignKeyProtect(Demand, null=True, blank=True)
    item = ForeignKeyProtect(Item)
    parent_launch = ForeignKeyProtect(Launches, null=True, blank=True, related_name='Production_order_opers_per_demand_parent_launch')
    launch = ForeignKeyProtect(Launches, related_name='Production_order_opers_per_demand_launch')
    color = ForeignKeyProtect(Standard_colors, null=True, blank=True)
    edizm = ForeignKeyProtect(Ed_izm)
    value_made = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)

    objects = Production_order_opers_per_demandManager()

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return self.__str__()

    class Meta:
        managed = False
        db_table = 'planing_production_order_per_demand_view'
        verbose_name = 'Операции Заказа на производство'
