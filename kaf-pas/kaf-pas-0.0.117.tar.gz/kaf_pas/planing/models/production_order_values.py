import logging

from django.conf import settings
from django.db import transaction
from django.db.models import DateTimeField, DecimalField

from isc_common import setAttr
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.base_ref import Hierarcy
from isc_common.models.standard_colors import Standard_colors
from isc_common.number import DelProps, DecimalToStr
from isc_common.ws.webSocket import WebSocket
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.planing.models.operation_refs import Operation_refsManager
from kaf_pas.planing.models.operation_types import Operation_types
from kaf_pas.planing.models.operations import OperationsManager, OperationsQuerySet, Operations
from kaf_pas.planing.operation_typesStack import MADE_OPRS_MNS_TSK, DETAIL_OPERS_PRD_TSK
from kaf_pas.production.models.launches import Launches
from kaf_pas.sales.models.demand import Demand

logger = logging.getLogger(__name__)


class Production_order_valuesQuerySet(OperationsQuerySet):
    def get_range_rows1(self, request, function=None, distinct_field_names=None, remove_fields=None):
        request = DSRequest(request=request)

        parent_id = request.get_data().get('parent_id')
        if parent_id is None:
            request.set_data(dict(parent_id=0))

        self.alive_only = request.alive_only
        self.enabledAll = request.enabledAll
        res = self.get_range_rows3(
            start=request.startRow,
            end=request.endRow,
            function=function,
            distinct_field_names=distinct_field_names,
            json=request.json,
            criteria=request.get_criteria(),
            user=request.user
        )
        # import time
        # time.sleep(1)
        return res


class Production_order_valuesManager(OperationsManager):
    @staticmethod
    def refreshRows(ids):
        if isinstance(ids, int):
            ids = [ids]
        records = [Production_order_valuesManager.getRecord(record) for record in Production_order_values.objects.filter(id__in=ids)]
        WebSocket.row_refresh_grid(grid_id=settings.GRID_CONSTANTS.refresh_production_order_operationsValues_grid_row, records=records)

    @staticmethod
    def fullRows(suffix=''):
        WebSocket.full_refresh_grid(grid_id=f'{settings.GRID_CONSTANTS.refresh_production_order_operationsValues_grid}{suffix}')

    def createFromRequest(self, request, removed=None):
        from kaf_pas.planing.models.production_order_values_ext import Production_order_values_ext
        from kaf_pas.planing.models.production_order import Production_orderManager

        request = DSRequest(request=request)
        data = request.get_data()

        if not isinstance(data.get('childs'), list):
            raise Exception('Не выбраны производственные операции(ия).')

        if not isinstance(data.get('parent_id'), int):
            raise Exception('Не выбран заказ на производство.')

        if data.get('edizm__code') is not None:
            setAttr(data, 'edizm_id', Ed_izm.objects.get(code=data.get('edizm__code')).id)

        if not isinstance(data.get('edizm_id'), int):
            raise Exception('Не указана единица измерения.')

        production_order, all_operations = None, None

        with transaction.atomic():
            try:
                production_order_values_ext = Production_order_values_ext()
                production_order, all_operations = production_order_values_ext.makeAll(
                    data=data,
                    user=request.user
                )
            except Exception as ex:
                raise ex

        Production_orderManager.update_redundant_planing_production_order_table(ids=production_order)
        Production_orderManager.refresh_all(
            buffer_refresh=True,
            ids=production_order,
            item_operations_refresh=True,
            production_order_values_refresh=True,
            production_order_opers_refresh=True,
            production_order_opers_ids=all_operations,
            user=request.user
        )
        return production_order

    def createBlockFromRequest(self, request, removed=None):
        from kaf_pas.planing.models.production_order_values_ext import Production_order_values_ext

        request = DSRequest(request=request)
        data = request.get_data()

        production_order_values_ext = Production_order_values_ext()

        res = production_order_values_ext.blockMakeAll(
            data=data,
            user=request.user
        )

        return res

    def deleteFromRequest(self, request, removed=None):
        from kaf_pas.planing.models.production_order_values_ext import Production_order_values_ext
        from kaf_pas.planing.models.production_order import Production_orderManager

        request = DSRequest(request=request)
        res = 0

        if request.tag is None:
            return res

        production_order_values_ext = Production_order_values_ext()

        data = request.get_old_data()
        try:
            operations = []
            operations.append(Operations.objects.get(id=data.get('id')))

            parentRecord = Operations.objects.get(id=request.tag.parentRecord)
            record_ids = request.tag.operationRecords

            with transaction.atomic():
                if production_order_values_ext.delete_sums(operations=operations, parent=parentRecord) > 0:
                    Production_orderManager.refresh_all(
                        buffer_refresh=True,
                        ids=parentRecord.id,
                        item_operations_refresh=True,
                        production_order_values_refresh=True,
                        production_order_opers_refresh=True,
                        production_order_opers_ids=record_ids,
                        user=request.user
                    )
        except Operations.DoesNotExist:
            raise Exception('Недейтсвительные данные, обновите грид.')

        return res

    @staticmethod
    def getRecord(record, enable):

        if enable == False:
            if record.opertype.is_minus:
                enable = False
            elif record.opertype.is_grouping:
                enable = False
            else:
                enable = True

        res = {
            'id': record.id,
            'color__color': record.color.color if record.color else None,
            'color__name': record.color.name if record.color else None,
            'color_id': record.color.id if record.color else None,

            'launch__code': record.launch.code if record.launch else None,
            'launch__date': record.launch.date if record.launch else None,
            'launch_id': record.launch.id if record.launch else None,

            'demand__code': record.demand.code if record.demand else None,
            'demand__date': record.demand.date if record.demand else None,
            'demand_id': record.demand.id if record.demand else None,

            'creator__short_name': record.creator.get_short_name,
            'creator_id': record.creator.id,
            'date': record.date,
            'edizm__name': record.edizm.name,
            'edizm_id': record.edizm.id,
            'enabled': enable,
            'value': DecimalToStr(record.value) if not record.opertype.is_minus else None,
            # 'value_minus': blinkString(text=DecimalToStr(-record.value), blink=False, color=red) if record.opertype.is_minus else None,
            'value_minus': DecimalToStr(-record.value) if record.opertype.is_minus else None,
        }
        return DelProps(res)

    def get_queryset(self):
        return Production_order_valuesQuerySet(self.model, using=self._db)


class Production_order_values(Hierarcy):
    color = ForeignKeyProtect(Standard_colors, null=True, blank=True)
    launch = ForeignKeyProtect(Launches, null=True, blank=True)
    demand = ForeignKeyProtect(Demand, null=True, blank=True)
    opertype = ForeignKeyProtect(Operation_types)
    operation = ForeignKeyProtect(Operations)
    creator = ForeignKeyProtect(User)
    edizm = ForeignKeyProtect(Ed_izm)
    date = DateTimeField()
    value = DecimalField(decimal_places=4, max_digits=19)
    props = Operation_refsManager.props()

    objects = Production_order_valuesManager()

    @property
    def get_pair_minus(self):
        from kaf_pas.planing.models.operation_refs import Operation_refs
        res = Operation_refs.objects.filter(child=self.operation, parent__opertype__code=MADE_OPRS_MNS_TSK)
        if res.count() == 0:
            return None
        elif res.count() > 1:
            raise Exception(f'Must be 0ne operation')
        else:
            return res[0].parent

    @property
    def tech_operation(self):
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.models.production_order_opers import Production_order_opers

        parent = Operation_refs.objects.filter(child_id=self.id, parent__opertype__code__in=[DETAIL_OPERS_PRD_TSK])[0].parent
        return Production_order_opers.objects.get(id=parent.id)

    @property
    def grouping_operation(self):
        from kaf_pas.planing.models.operation_refs import Operation_refs
        return Production_order_values.objects.filter(parent_id=self.id, props=Operation_refs.props.product_making_block)

    def clone(self):
        cl = Operations.objects.get(id=self.id)
        cl.pk = None
        cl.save()
        return cl

    def __str__(self):
        return f'\n\n--values\nid: {self.id}, date:{self.date}, value: {self.value}' \
               f'color: [{self.color}],' \
               f' opertype: [{self.opertype}], ' \
               f'operation: [{self.operation}], ' \
               f'creator: [{self.creator}], edizm: [{self.edizm}]'

    def __repr__(self):
        return self.__str__()

    class Meta:
        managed = False
        db_table = 'planing_operations_values_view'
        verbose_name = 'Списания'
