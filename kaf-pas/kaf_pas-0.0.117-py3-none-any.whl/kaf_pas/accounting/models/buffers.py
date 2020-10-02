import logging

from django.conf import settings
from django.db.models import DecimalField, Model, DateField

import kaf_pas
from isc_common import Wrapper
from isc_common.common import blinkString
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditManager, AuditQuerySet
from isc_common.models.standard_colors import Standard_colors
from isc_common.number import DelProps, DecimalToStr
from isc_common.ws.webSocket import WebSocket
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.planing.models.operations import Operations
from kaf_pas.production.models.launches import Launches
from kaf_pas.production.models.resource import Resource
from kaf_pas.sales.models.demand import Demand

logger = logging.getLogger(__name__)


class BWrapper(Wrapper):
    pass

class BufferQuerySet(AuditQuerySet):
    def get_range_rows1(self, request, function=None, distinct_field_names=None, remove_fields=None):
        request = DSRequest(request=request)

        data = request.get_data()

        request.set_data(data=data)

        res = self.get_range_rows(
            start=request.startRow,
            end=request.endRow,
            function=function,
            distinct_field_names=distinct_field_names,
            json=request.json,
            criteria=request.get_criteria(),
            user=request.user
        )
        return res


class BuffersManager(AuditManager):
    def get_queryset(self):
        return BufferQuerySet(model=self.model)

    @staticmethod
    def refreshRows(ids):
        if isinstance(ids, int):
            ids = [ids]
        records = [BuffersManager.getRecord(record) for record in Buffers.objects.filter(id__in=ids)]
        WebSocket.row_refresh_grid(grid_id=settings.GRID_CONSTANTS.refresh_production_buffers_grid_row, records=records)

    @staticmethod
    def fullRows(suffix=''):
        WebSocket.full_refresh_grid(grid_id=f'{settings.GRID_CONSTANTS.refresh_production_buffers_grid}{suffix}')

    @staticmethod
    def get_buffer_oddment_value(value):
        if value is None:
            return 0
        return blinkString(text=DecimalToStr(value), blink=True if value < 0 else False, bold=True, color='green' if value > 0 else 'red')

    @staticmethod
    def getValue(item, color=None):
        try:
            buffer = Buffers.objects.get(item=item)
            return buffer.value if buffer.value else 0
        except Buffers.DoesNotExist:
            return None

    @staticmethod
    def getRecord(record):
        res = {
            # 'resource_id': record.resource.id if record.resource else None,
            'location_code': record.location_code,
            'location_full_name': record.location_full_name,
            'item_id': record.item.id,
            'value': BuffersManager.get_buffer_oddment_value(record.value),
            'value_real': DecimalToStr(record.value),
            'demand_id': record.demand.id if record.demand else None,
            'demand__code': record.demand.code if record.demand else None,
            'demand__date': record.demand.date if record.demand else None,
            'launch_id': record.launch.id if record.launch else None,
            'launch__code': record.launch.code if record.launch else None,
            'launch__date': record.launch.date if record.launch else None,
            'color_id': record.color.id if record.color else None,
            'color__color': record.color.color if record.color else None,
            'color__name': record.color.name if record.color else None,
            'item__STMP_1_id': record.item.STMP_1.id if record.item.STMP_1 else None,
            'item__STMP_1__value_str': record.item.STMP_1.value_str if record.item.STMP_1 else None,
            'item__STMP_2_id': record.item.STMP_2.id if record.item.STMP_2 else None,
            'item__STMP_2__value_str': record.item.STMP_2.value_str if record.item.STMP_2 else None,

            'edizm_id': record.edizm.id,
            'edizm__code': record.edizm.code,
            'edizm__name': record.edizm.name,

            'last_operation_full_name': record.last_operation_full_name
        }
        return DelProps(res)


class Buffers(Model):
    color = ForeignKeyProtect(Standard_colors, null=True, blank=True)
    deleted_at = DateField(null=True, blank=True)
    demand = ForeignKeyProtect(Demand, null=True, blank=True)
    edizm = ForeignKeyProtect(Ed_izm, null=True, blank=True)
    item = ForeignKeyProtect(Item)
    last_tech_operation = ForeignKeyProtect(Operations, null=True, blank=True)
    last_operation = ForeignKeyProtect(kaf_pas.production.models.operations.Operations, null=True, blank=True)
    last_operation_full_name = NameField(null=True, blank=True)
    launch = ForeignKeyProtect(Launches, null=True, blank=True)
    resource = ForeignKeyProtect(Resource, null=True, blank=True)
    location = ForeignKeyProtect(Locations, null=True, blank=True)
    location_code = NameField(null=True, blank=True)
    location_full_name = NameField(null=True, blank=True)
    value = DecimalField(decimal_places=4, max_digits=19)

    objects = BuffersManager()

    def __str__(self):
        return f'item: [{self.item}], ' \
               f'color: [{self.color}] , ' \
               f'value: [{self.value}] , ' \
               f'demand: [{self.demand}] , ' \
               f'edizm: [{self.edizm}] , ' \
               f'launch: [{self.launch}] , location: [{self.location}] , ' \
               f'last_operation: [{self.last_operation}] '

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Буферы'
        managed = False
        db_table = 'accounting_buffers_view'
