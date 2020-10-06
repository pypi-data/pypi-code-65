import logging

from bitfield import BitField
from django.db import transaction
from django.db.models import DecimalField, TextField
from django.forms import model_to_dict

from isc_common import delAttr, setAttr
from isc_common.auth.models.user import User
from isc_common.common import blinkString, red
from isc_common.fields.related import ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditModel
from isc_common.models.standard_colors import Standard_colors
from isc_common.number import DelProps, ToDecimal
from kaf_pas.accounting.models.buffers import BuffersManager
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.production.models.launches import Launches
from kaf_pas.production.models.resource import Resource
from kaf_pas.sales.models.demand import Demand

logger = logging.getLogger(__name__)


class Tmp_bufferQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    pass


class Tmp_bufferManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def props():
        return BitField(flags=(
            ('posting_nakl', 'Оприходования из накладной'),  # 1
            ('posting_uqv', 'Оприходования из минусов'),  # 1
            ('write_off', 'Списания'),  # 2
        ), db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'color__color': record.color.color if record.color else None,
            'color__name': record.color.name if record.color else None,
            'color_id': record.color.id if record.color else None,
            'deliting': record.deliting,
            'demand__code': record.demand.code if record.demand else None,
            'demand__date': record.demand.date if record.demand else None,
            'demand_id': record.demand.id if record.demand else None,
            'description': record.description,
            'editing': record.editing,
            'edizm__code': record.edizm.code,
            'edizm__name': record.edizm.name,
            'edizm_id': record.edizm.id,
            'id': record.id,
            'item__STMP_1__value_str': record.item.STMP_1.value_str if record.item.STMP_1 else None,
            'item__STMP_1_id': record.item.STMP_1.id if record.item.STMP_1 else None,
            'item__STMP_2__value_str': record.item.STMP_2.value_str if record.item.STMP_2 else None,
            'item__STMP_2_id': record.item.STMP_2.id if record.item.STMP_2 else None,
            'item_id': record.item.id,
            'launch__code': record.launch.code if record.launch else None,
            'launch__date': record.launch.date if record.launch else None,
            'launch_id': record.launch.id if record.launch else None,
            'location__code': record.location.code,
            'location__full_name': record.location.full_name,
            'location__name': record.location.name,
            'location_id': record.location.id,
            'value': BuffersManager.get_buffer_oddment_value(record.value),
            'value_num': ToDecimal(record.value),
            'value_off': ToDecimal(record.value_off),
        }
        return res

    def createFromRequest(self, request, removed=None):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()

        if data.get('item_id') is None:
            raise Exception('Не выбрана товарная позиция.')

        delAttr(_data, 'dataSource')
        delAttr(_data, 'operationType')
        delAttr(_data, 'textMatchStyle')
        delAttr(_data, 'form')
        setAttr(_data, 'user_id', request.user_id)
        self._remove_prop(_data, removed)

        res = super().create(**_data)
        res = model_to_dict(res)
        setAttr(res, 'full_name', res.full_name)

        setAttr(res, 'isFolder', False)
        data.update(DelProps(res))
        return data

    def updateFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()

        _data = data.copy()

        value_off = ToDecimal(data.get('value_off'))
        value_num = abs(ToDecimal(data.get('value_num')))

        if value_off > 0:
            if value_num < value_off:
                raise Exception(f'''У {blinkString(Item.objects.get(id=data.get('item_id')).item_name, color=red, bold=True)} Превышен cумма, введено {value_off} при возможной {value_num}''')

        delAttr(_data, 'id')
        delAttr(_data, 'item')
        delAttr(_data, 'location')
        delAttr(_data, 'user')
        delAttr(_data, 'edizm')
        delAttr(_data, 'color__color')
        delAttr(_data, 'color__name')
        delAttr(_data, 'edizm__code')
        delAttr(_data, 'edizm__name')
        delAttr(_data, 'item__STMP_1__value_str')
        delAttr(_data, 'item__STMP_2__value_str')
        delAttr(_data, 'item__STMP_1_id')
        delAttr(_data, 'item__STMP_2_id')
        delAttr(_data, 'location__code')
        delAttr(_data, 'location__name')
        delAttr(_data, 'location__full_name')
        setAttr(_data, 'value', value_num)
        setAttr(data, 'value', value_num)
        delAttr(_data, 'value_num')
        setAttr(_data, 'user_id', request.user_id)
        setAttr(_data, 'props', 1)

        # setAttr(data,'id', res.id)
        return data

    def update_offFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()

        # _data = data.copy()

        value_off = ToDecimal(data.get('value_off'))
        value_num = abs(ToDecimal(data.get('value_num')))

        if value_off > 0:
            if value_num < value_off:
                raise Exception(f'''У {blinkString(Item.objects.get(id=data.get('item_id')).item_name, color=red, bold=True)} Превышен cумма, введено {value_off} при возможной {value_num}''')

        res = super().get(id=data.get('id'))
        res.value_off = data.get('value_off')
        res.save()

        return data

    def deleteFromRequest(self, request, removed=None, ):
        request = DSRequest(request=request)
        res = 0
        tuple_ids = request.get_tuple_ids()
        with transaction.atomic():
            for id, mode in tuple_ids:
                if mode == 'hide':
                    super().filter(id=id).soft_delete()
                elif mode == 'visible':
                    super().filter(id=id).soft_restore()
                else:
                    qty, _ = super().filter(id=id).delete()
                res += qty
        return res

    def get_queryset(self):
        return Tmp_bufferQuerySet(self.model, using=self._db)


class Tmp_buffer(AuditModel):
    color = ForeignKeyCascade(Standard_colors, null=True, blank=True)
    demand = ForeignKeyCascade(Demand, null=True, blank=True)
    launch = ForeignKeyCascade(Launches, null=True, blank=True)
    description = TextField(null=True, blank=True)
    edizm = ForeignKeyCascade(Ed_izm)
    item = ForeignKeyCascade(Item)
    location = ForeignKeyCascade(Locations)
    props = Tmp_bufferManager.props()
    user = ForeignKeyCascade(User)
    value = DecimalField(max_digits=19, decimal_places=4)
    value_off = DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)

    objects = Tmp_bufferManager()

    def __str__(self):
        return f'ID: {self.id}, ' \
               f'value: {self.value}, ' \
               f'value_off: {self.value_off}, ' \
               f'color: [{self.color}], ' \
               f'description: [{self.description}], ' \
               f'demand: {self.demand}, ' \
               f'edizm: [{self.edizm}], ' \
               f'item: [{self.item}], ' \
               f'location: [{self.location}], ' \
               f'user: [{self.user}], ' \
               f'resource: [{self.resource}]'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Временное хранилищи данных для буферов'
