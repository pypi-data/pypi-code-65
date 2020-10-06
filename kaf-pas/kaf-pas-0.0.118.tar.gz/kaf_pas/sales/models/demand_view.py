import logging

from django.db.models import PositiveIntegerField, DateTimeField, BooleanField, DecimalField

from isc_common.bit import IsBitOff
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.base_ref import BaseRefHierarcy
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.sales.models.precent import Precent
from kaf_pas.sales.models.precent_dogovors import Precent_dogovors
from kaf_pas.sales.models.precent_items import Precent_items
from kaf_pas.sales.models.status_demand import Status_demand

logger = logging.getLogger(__name__)


class Demand_viewQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    pass


class Demand_viewManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'parent': record.parent.id if record.parent else None,
            'date': record.date,
            'date_sign': record.precent.date_sign,
            'qty': record.qty,
            'launch_qty': record.launch_qty,
            'tail_qty': record.tail_qty,
            'qty_for_launch': record.qty_for_launch,
            'parent_id': record.parent.id if record.parent else None,

            'precent_id': record.precent.id,
            'precent__code': record.precent.code,
            'precent__date': record.precent.date,

            'precent__precent_type_id': record.precent.precent_type.id,
            'precent__precent_type__name': record.precent.precent_type.name,

            'precent_dogovor_id': record.precent_dogovor.id,
            'precent_dogovor__code': record.precent_dogovor.dogovor.code,
            'precent_dogovor__name': record.precent_dogovor.dogovor.name,
            'precent_dogovor__date': record.precent_dogovor.dogovor.date,

            'precent_dogovor__dogovor__customer__name': record.precent_dogovor.dogovor.customer.name,

            'precent_item_id': record.precent_item.id,
            'precent_item__STMP_1_id': record.precent_item.item.STMP_1.id if record.precent_item.item.STMP_1 else None,
            'precent_item__STMP_1__value_str': record.precent_item.item.STMP_1.value_str if record.precent_item.item.STMP_1 else None,
            'precent_item__STMP_2_id': record.precent_item.item.STMP_2.id if record.precent_item.item.STMP_2 else None,
            'precent_item__STMP_2__value_str': record.precent_item.item.STMP_2.value_str if record.precent_item.item.STMP_2 else None,

            'status_id': record.status.id,
            'status__code': record.status.code,
            'status__name': record.status.name,

            'isFolder': record.isFolder,
            'enabled': IsBitOff(record.status.props, 0),

            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    @staticmethod
    def getRecord1(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'parent': record.parent.id if record.parent else None,
            'date': record.date,
            'date_sign': record.precent.date_sign,
            'qty': record.qty,
            'launch_qty': record.launch_qty,
            'tail_qty': record.tail_qty,
            'qty_for_launch': record.qty_for_launch,
            'parent_id': record.parent.id if record.parent else None,
            'enabled' : record.launch_qty < record.tail_qty,

            'precent_id': record.precent.id,
            'precent__code': record.precent.code,
            'precent__date': record.precent.date,

            'precent__precent_type_id': record.precent.precent_type.id,
            'precent__precent_type__name': record.precent.precent_type.name,

            'precent_dogovor_id': record.precent_dogovor.id,
            'precent_dogovor__code': record.precent_dogovor.dogovor.code,
            'precent_dogovor__name': record.precent_dogovor.dogovor.name,
            'precent_dogovor__date': record.precent_dogovor.dogovor.date,

            'precent_dogovor__dogovor__customer__name': record.precent_dogovor.dogovor.customer.name,

            'precent_item_id': record.precent_item.id,
            'precent_item__STMP_1_id': record.precent_item.item.STMP_1.id if record.precent_item.item.STMP_1 else None,
            'precent_item__STMP_1__value_str': record.precent_item.item.STMP_1.value_str if record.precent_item.item.STMP_1 else None,
            'precent_item__STMP_2_id': record.precent_item.item.STMP_2.id if record.precent_item.item.STMP_2 else None,
            'precent_item__STMP_2__value_str': record.precent_item.item.STMP_2.value_str if record.precent_item.item.STMP_2 else None,

            'status_id': record.status.id,
            'status__code': record.status.code,
            'status__name': record.status.name,

            'isFolder': record.isFolder,

            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Demand_viewQuerySet(self.model, using=self._db)


class Demand_view(BaseRefHierarcy):
    date = DateTimeField()
    isFolder = BooleanField()
    launch_qty = PositiveIntegerField()
    precent = ForeignKeyCascade(Precent)
    precent_dogovor = ForeignKeyCascade(Precent_dogovors)
    precent_item = ForeignKeyCascade(Precent_items)
    qty = PositiveIntegerField()
    qty_for_launch = PositiveIntegerField(null=True, blank=True)
    status = ForeignKeyProtect(Status_demand)
    tail_qty = PositiveIntegerField()
    STMP_1 = ForeignKeyProtect(Document_attributes, related_name='Demand_view_STMP_1', null=True, blank=True)
    STMP_2 = ForeignKeyProtect(Document_attributes, related_name='Demand_view_STMP_2', null=True, blank=True)

    objects = Demand_viewManager()

    def __str__(self):
        return f"ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}"

    @property
    def year_month(self):
        return f'{self.year} / {self.month}'

    class Meta:
        verbose_name = 'Заказы на продажу'
        db_table = 'sales_demand_view'
        managed = False
