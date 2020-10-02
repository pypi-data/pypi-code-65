import logging

from django.conf import settings
from django.db.models import DateTimeField, BooleanField, DecimalField, PositiveIntegerField

from isc_common import setAttr
from isc_common.common import blinkString, green
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.isc.data_binding.advanced_criteria import AdvancedCriteria
from isc_common.models.base_ref import BaseRefHierarcy, BaseRefManager, BaseRefQuerySet
from isc_common.number import DelProps, DecimalToStr
from isc_common.ws.webSocket import WebSocket
from kaf_pas.ckk.models.item import Item
from kaf_pas.planing.models.production_order_values_ext import Production_orderWrapper
from kaf_pas.planing.operation_typesStack import NoLaunch
from kaf_pas.production.models.status_launch import Status_launch
from kaf_pas.sales.models.demand import Demand

logger = logging.getLogger(__name__)


class Launches_viewQuerySet(BaseRefQuerySet):

    def get_range_rows_4_Production_values(self, request, function=None, distinct_field_names=None, remove_fields=None):
        from kaf_pas.accounting.models.buffers import Buffers
        from kaf_pas.production.models.launch_item_refs import Launch_item_refs
        from kaf_pas.production.models.launch_item_prod_order_per_launch_view import Launch_item_prod_order_per_launch_view

        request = DSRequest(request=request)

        res = []

        if len(request.get_criteria()) > 0:
            advancedCriteria = AdvancedCriteria(lst=request.get_criteria())

            if isinstance(advancedCriteria.criteria, list):
                if len(advancedCriteria.criteria) == 0:
                    raise Exception('Не сделан выбор')

            if isinstance(advancedCriteria.criteria[0].value, dict):
                record_0 = Production_orderWrapper(**advancedCriteria.criteria[0].value)
                production_operation_num = record_0.production_operation_num

                for buffers_item in Buffers.objects.filter(item=record_0.item, last_operation=record_0.childs[production_operation_num - 2].production_operation):
                    value_odd = buffers_item.value

                    if value_odd > 0:
                        record = Launches_viewManager.getRecord(Launches_view.objects.get(id=buffers_item.launch.id))
                    res.append(setAttr(record, 'value_odd', DecimalToStr(value_odd)))
        else:
            data = request.get_data()
            if isinstance(data, dict):
                operations = data.get('operations')
                if isinstance(operations, list):
                    for operation in operations:
                        record_0 = Production_orderWrapper(**operation)

                        if record_0.production_operation_num == 1:
                            launches = set(map(lambda x: x.launch.id, Launch_item_refs.tree_objects.get_descendants(id=record_0.item.id)))
                            for launche_view_item in Launches_view.objects.filter(id__in=launches):
                                record = Launches_viewManager.getRecord(launche_view_item)

                                for launch_item_order in Launch_item_prod_order_per_launch_view.objects.filter(
                                        item=record_0.item,
                                        launch_id=launche_view_item.id
                                ):
                                    if launch_item_order.qty_odd > 0:
                                        res.append(setAttr(record, 'value_odd', blinkString(DecimalToStr(launch_item_order.qty_odd), blink=False, color=green, bold=True)))
                                    # else:
                                    #     res.append(setAttr(record, 'value_odd', blinkString(DecimalToStr(launch_item_order.qty_odd), blink=True, color=red, bold=True)))
                        else:
                            for buffers_item in Buffers.objects.filter(item=record_0.item, last_operation=record_0.childs[record_0.production_operation_num - 2].production_operation):
                                value_odd = buffers_item.value

                                if value_odd > 0:
                                    record = Launches_viewManager.getRecord(Launches_view.objects.get(id=buffers_item.launch.id))
                                    res.append(setAttr(record, 'value_odd', blinkString(DecimalToStr(value_odd), blink=False, color=green, bold=True)))

        return res


class Launches_viewManager(BaseRefManager):

    @staticmethod
    def refreshRows(ids):
        if isinstance(ids, int):
            ids = [ids]
        records = [Launches_viewManager.getRecord(record) for record in Launches_view.objects.filter(id__in=ids)]
        WebSocket.row_refresh_grid(grid_id=settings.GRID_CONSTANTS.refresh_production_launch_grid_row, records=records)

    @staticmethod
    def fullRows(suffix=''):
        WebSocket.full_refresh_grid(grid_id=f'{settings.GRID_CONSTANTS.refresh_production_launch_grid}{suffix}')

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'date': record.date if record.code != NoLaunch else None,
            'description': record.description,
            'parent_id': record.parent.id if record.parent else None,

            'demand_id': record.demand.id if record.demand else None,
            'demand__code': record.demand.code if record.demand else None,
            'demand__date': record.demand.date if record.demand else None,

            'item_id': record.item.id if record.item else None,
            'parent_item_id': record.parent_item.id if record.parent_item else None,
            'item__STMP_1_id': record.item.STMP_1.id if record.item and record.item.STMP_1 else None,
            'item__STMP_1__value_str': record.item.STMP_1.value_str if record.item and record.item.STMP_1 else None,
            'item__STMP_2_id': record.item.STMP_2.id if record.item and record.item.STMP_2 else None,
            'item__STMP_2__value_str': record.item.STMP_2.value_str if record.item and record.item.STMP_2 else None,

            'status_id': record.status.id,
            'status__code': record.status.code,
            'status__name': record.status.name if record.code != '000' else '',

            'qty': DecimalToStr(record.qty),
            'qty_made': record.qty_made,
            'value_made': record.value_made,
            'value_sum': record.value_sum,
            # 'qty_need': record.qty_need,
            'isFolder': record.isFolder,
            'priority': record.priority if record.parent else '',
            # 'props': record.props,

            'editing': record.editing,
            'deliting': record.deliting,
            'isDeleted': record.isDeleted,
        }
        res = DelProps(res)
        # print(res)
        return res

    def get_queryset(self):
        return Launches_viewQuerySet(self.model, using=self._db)


class Launches_view(BaseRefHierarcy):
    # props = LaunchesManager.props()
    date = DateTimeField()
    demand = ForeignKeyProtect(Demand, null=True, blank=True)
    isFolder = BooleanField()
    isDeleted = BooleanField()
    item = ForeignKeyProtect(Item, null=True, blank=True, related_name='Launches_view_item')
    parent_item = ForeignKeyProtect(Item, null=True, blank=True, related_name='Launches_view_parent_item')
    priority = PositiveIntegerField(db_index=True, default=0)
    qty = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    status = ForeignKeyProtect(Status_launch)
    value_made = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    value_sum = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)

    objects = Launches_viewManager()

    @property
    def qty_made(self):
        res = 0
        logger.debug(f'qty_made: {res}')
        return res

    @property
    def qty_need(self):
        res = self.qty - self.qty_made if self.qty else 0
        logger.debug(f'qty_need: {res}')
        return res

    def __str__(self):
        return f"ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}"

    class Meta:
        verbose_name = 'Запуски'
        db_table = 'production_launches_view'
        managed = False
