import logging

from django.db import transaction
from django.db.models import PositiveIntegerField, DateTimeField, DecimalField

from isc_common import delAttr, setAttr
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.base_ref import BaseRefHierarcy
from kaf_pas.sales.models.precent import Precent
from kaf_pas.sales.models.precent_dogovors import Precent_dogovors
from kaf_pas.sales.models.precent_items import Precent_items
from kaf_pas.sales.models.precent_items_view import Precent_items_view
from kaf_pas.sales.models.status_demand import Status_demand

logger = logging.getLogger(__name__)


class DemandQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def get_info(self, request, *args):
        request = DSRequest(request=request)
        delAttr(request.json.get('data'), 'full_name')
        criteria = self.get_criteria(json=request.json)
        cnt = super().filter(*args, criteria).count()
        cnt_all = super().filter().count()
        return dict(qty_rows=cnt, all_rows=cnt_all)


class DemandManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'parent': record.parent.id if record.parent else None,
            'date': record.date,
            'date_sign': record.date_sign,
            'qty': record.qty,
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
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return DemandQuerySet(self.model, using=self._db)

    def createFromRequest(self, request):
        from kaf_pas.sales.models.demand_materials import Demand_materials
        from django.conf import settings
        from kaf_pas.sales.models.precent_materials import Precent_materials

        request = DSRequest(request=request)
        key = 'DemandManager.createFromRequest'

        settings.LOCKS.acquire(key)
        data = request.get_data()
        _data = data.copy()

        try:

            precent = _data.get('precent')
            if precent:
                with transaction.atomic():
                    precent_id = precent.get('precent_id')
                    setAttr(_data, 'precent_id', precent_id)
                    precent_dogovor_id = precent.get('precent_dogovor_id')
                    setAttr(_data, 'precent_dogovor_id', precent_dogovor_id)
                    precent_item_id = precent.get('precent_item_id')
                    setAttr(_data, 'precent_item_id', precent_item_id)
                    delAttr(_data, 'precent')
                    delAttr(_data, 'precent_material_id')
                    _qty = _data.get('qty')

                    for precent_item in Precent_items.objects.filter(id=precent_item_id).select_for_update():
                        precent_item = Precent_items_view.objects.get(id=precent_item.id)
                        qty = precent_item.qty - precent_item.used_qty
                        if _qty > qty:
                            raise Exception(f'Нет затребованного количества. В наличии {qty}, затребовано: {_qty}')
                        res = super().create(**_data)
                        setAttr(_data, 'id', res.id)

                        precent_material_ids = precent.get('precent_material_ids')
                        if isinstance(precent_material_ids, list):
                            for precent_material_id in precent_material_ids:
                                precent_materials = Precent_materials.objects.get(id=precent_material_id)
                                Demand_materials.objects.get_or_create(
                                    demand=res,
                                    material_id=precent_material_id,
                                    qty=precent_materials.qty,
                                    edizm=precent_materials.edizm,
                                )

            return _data
            settings.LOCKS.release(key)
        except Exception as ex:
            settings.LOCKS.release(key)
            raise ex


    def updateFromRequest(self, request, removed=None, function=None):
        request = DSRequest(request=request)
        data = request.get_data()

        _data = data.copy()
        with transaction.atomic():
            if data.get('launch_qty') > data.get('qty'):
                raise Exception(f'Сделать количетво менее чем запущенное, нельзя.')
            delAttr(_data, 'date_sign')
            delAttr(_data, 'launch_qty')
            delAttr(_data, 'tail_qty')
            delAttr(_data, 'enabled')
            delAttr(_data, 'parent')
            delAttr(_data, 'precent__code')
            delAttr(_data, 'precent__date')
            delAttr(_data, 'precent__precent_type_id')
            delAttr(_data, 'precent__precent_type__name')
            delAttr(_data, 'precent_dogovor__code')
            delAttr(_data, 'precent_dogovor__name')
            delAttr(_data, 'precent_dogovor__date')
            delAttr(_data, 'precent_dogovor__dogovor__customer__name')
            delAttr(_data, 'precent_item__STMP_1_id')
            delAttr(_data, 'precent_item__STMP_1__value_str')
            delAttr(_data, 'precent_item__STMP_2_id')
            delAttr(_data, 'precent_item__STMP_2__value_str')
            delAttr(_data, 'status__code')
            delAttr(_data, 'status__name')
            delAttr(_data, 'isFolder')
            delAttr(_data, 'year')
            delAttr(_data, 'month')
            delAttr(_data, 'month_name')
            delAttr(_data, 'groupParentId')
            super().filter(id=data.get('id')).update(**_data)

        return data


class Demand(BaseRefHierarcy):
    date = DateTimeField(verbose_name='Дата')
    date_sign = DateTimeField(verbose_name='Срок поставки', db_index=True, null=True, blank=True)
    precent = ForeignKeyCascade(Precent)
    precent_dogovor = ForeignKeyCascade(Precent_dogovors)
    precent_item = ForeignKeyCascade(Precent_items)
    status = ForeignKeyProtect(Status_demand)
    qty = PositiveIntegerField()
    qty_for_launch = PositiveIntegerField(null=True, blank=True)

    objects = DemandManager()

    def __str__(self):
        return f"ID:{self.id}, " \
               f"code: {self.code}, " \
               f"name: {self.name}, " \
               f"description: {self.description}, " \
               f"status: [{self.status}], " \
               f"precent_item: [{self.precent_item}], " \
               f"precent_dogovor: [{self.precent_dogovor}], " \
               f"precent: [{self.precent}]"

    class Meta:
        verbose_name = 'Заказы на продажу'
