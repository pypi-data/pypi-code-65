import copy
import logging
from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import EmptyResultSet
from django.db import transaction, connection
from django.db.models import DecimalField, DateTimeField, TextField, BooleanField, BigIntegerField, PositiveIntegerField
from django.forms import model_to_dict

from isc_common import setAttr, delAttr, Stack
from isc_common.auth.models.user import User
from isc_common.common import blinkString, started, new, doing
from isc_common.common.functions import ExecuteStoredProc
from isc_common.datetime import DateTimeToStr
from isc_common.fields.code_field import CodeField, JSONFieldIVC
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_manager import CommonManager
from isc_common.models.base_ref import Hierarcy
from isc_common.number import DecimalToStr, ToDecimal, Set
from isc_common.ws.webSocket import WebSocket
from kaf_pas.ckk.models.item import Item
from kaf_pas.planing.models.operation_item_view import Operation_item_view
from kaf_pas.planing.models.operation_types import Operation_types
from kaf_pas.planing.models.operations import OperationsQuerySet, Operations
from kaf_pas.planing.models.production_ext import Production_ext, Operation_executor_stack
from kaf_pas.planing.models.rouning_ext import Routing_ext
from kaf_pas.production.models.launches import Launches

logger = logging.getLogger(__name__)


class Production_orderQuerySet(OperationsQuerySet):
    @staticmethod
    def get_user_locations(user):
        from kaf_pas.ckk.models.locations_users import Locations_users
        if not user.is_admin and not user.is_develop:
            return list(map(lambda x: x.location.id, Locations_users.objects.filter(user=user).distinct()))
        else:
            return None

    def check_state(self):
        for this in self:
            if ToDecimal(this.value_odd) > 0:
                status = settings.OPERS_TYPES_STACK.PRODUCTION_TASK_STATUSES.get(started)
            elif ToDecimal(this.value_start) == 0:
                status = settings.OPERS_TYPES_STACK.PRODUCTION_TASK_STATUSES.get(new)
            else:
                if ToDecimal(this.value_start) >= ToDecimal(this.value_sum):
                    status = settings.OPERS_TYPES_STACK.PRODUCTION_TASK_STATUSES.get(doing)
                else:
                    status = settings.OPERS_TYPES_STACK.PRODUCTION_TASK_STATUSES.get(started)

            updated = super().filter(id=this.id).update(status=status)
            logger.debug(f'updated: {updated}')
            updated = Operations.objects.filter(id=this.id).update(status=status)
            logger.debug(f'updated: {updated}')

    def get_range_rows(self, start=None, end=None, function=None, json=None, distinct_field_names=None, user=None, *args, **kwargs):
        queryResult = self._get_range_rows(*args, start=start, end=end, function=function, json=json, distinct_field_names=distinct_field_names)

        try:
            logger.debug(f'\n\n{queryResult.query}\n')
        except EmptyResultSet:
            pass

        if function:
            location_ids = Production_orderQuerySet.get_user_locations(user=user)
            res = [function(record, location_ids) for record in queryResult]
            return res
        else:
            res = [model_to_dict(record) for record in queryResult]
            return res

    def get_range_rows1(self, request, function=None, distinct_field_names=None, remove_fields=None, *args, **kwargs):
        request = DSRequest(request=request)
        data = request.get_data()

        _data = data.copy()

        delAttr(_data, 'arranged')
        delAttr(_data, 'location_id')

        request.set_data(_data)

        self.alive_only = request.alive_only
        self.enabledAll = request.enabledAll
        res = self.get_range_rows(
            start=request.startRow,
            end=request.endRow,
            function=function,
            distinct_field_names=distinct_field_names,
            json=request.json,
            criteria=request.get_criteria(),
            user=request.user,
        )
        return res

    def get_info(self, request, *args):
        request = DSRequest(request=request)
        data = request.get_data()

        launch_id = data.get('launch_id')
        delAttr(data, 'launch_id')

        location_id = data.get('location_id')
        delAttr(data, 'location_id')

        arranged = data.get('arranged')
        delAttr(data, 'arranged')

        json_all = dict()
        executor = None

        if not request.is_admin and not request.is_develop:
            executor = request.user

        if launch_id is not None:
            for launch in Launches.objects.filter(id=launch_id):
                if launch.parent is not None:
                    items = [operation_item_view.item for operation_item_view in Operation_item_view.objects.filter(
                        opertype_id=settings.OPERS_TYPES_STACK.ROUTING_TASK.id,
                        launch=launch).distinct()]
                    setAttr(request.json.get('data'), 'launch_id', launch.parent.id)
                    setAttr(request.json.get('data'), 'item', items)

                    json_all = copy.deepcopy(request.json)
                    delAttr(json_all.get('data'), 'location_id')
                    delAttr(json_all.get('data'), 'arranged')

        request.set_data(data)
        criteria = self.get_criteria(json=request.json)
        criteria_all = self.get_criteria(json=json_all)
        if executor is not None:
            if arranged:
                cnt = super(). \
                    filter(arranges_exucutors__overlap=[executor.id]).filter(*args, criteria). \
                    filter(location_ids__overlap=[location_id]).filter(*args, criteria). \
                    count()
                cnt_all = super().filter(arranges_exucutors__overlap=[executor.id]).filter(*args, criteria_all). \
                    filter(location_ids__overlap=[location_id]).filter(*args, criteria). \
                    count()
            else:
                cnt = super().filter(exucutors__overlap=[executor.id]).filter(*args, criteria). \
                    filter(location_ids__overlap=[location_id]).filter(*args, criteria). \
                    count()
                cnt_all = super().filter(exucutors__overlap=[executor.id]).filter(*args, criteria_all). \
                    filter(location_ids__overlap=[location_id]).filter(*args, criteria). \
                    count()
        else:
            if arranged:
                cnt = super(). \
                    filter(location_ids__overlap=[location_id]).filter(*args, criteria). \
                    count()
                cnt_all = super(). \
                    filter(location_ids__overlap=[location_id]).filter(*args, criteria). \
                    count()
            else:
                cnt = super().filter(*args, criteria). \
                    filter(location_ids__overlap=[location_id]).filter(*args, criteria). \
                    count()
                cnt_all = super().filter(*args, criteria_all). \
                    filter(location_ids__overlap=[location_id]).filter(*args, criteria). \
                    count()

        return dict(qty_rows=cnt, all_rows=cnt_all)

    def get_setStartStatus(self, request):
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.operation_typesStack import DETAIL_OPERS_PRD_TSK

        request = DSRequest(request=request)

        data = request.get_data()
        qty = data.get('qty')
        if qty is None:
            raise Exception('Не введено количество.')

        idx = 0
        _res = None
        production_ext = Production_ext()

        with transaction.atomic():
            operation_executor_stack = Operation_executor_stack()
            while True:
                _data = data.get(str(idx))
                if _data is None:
                    break
                idx += 1

                _res = production_ext.start(
                    _data=self.delete_underscore_element(_data),
                    qty=qty,
                    user=request.user,
                    operation_executor_stack=operation_executor_stack
                )

            ids = map(lambda x: x.get('id'), _res)
            for operation_executor in operation_executor_stack:
                if operation_executor.executor != request.user:
                    settings.EVENT_STACK.EVENTS_PRODUCTION_ORDER_CREATE.send_message(
                        message=blinkString(f'<h4>Вам направлено: {operation_executor.qty} новых заданий на производство.</h4>', bold=True),
                        users_array=[operation_executor.executor],
                    )
                    if len(_res) == 1:
                        Production_orderManager.refresh_all(
                            ids=ids,
                            suffix=f'''_user_id_{operation_executor.executor.id}''',
                            production_order_opers_refresh=True,
                            production_order_opers_ids=map(lambda x: x.child.id, Operation_refs.objects.filter(parent_id__in=ids, child__opertype__code__in=[DETAIL_OPERS_PRD_TSK])),
                            user=request.user
                        )

            if len(_res) > 1:
                Production_orderManager.refresh_all(
                    ids=ids,
                    production_order_opers_refresh=True,
                    production_order_opers_ids=map(lambda x: x.child.id, Operation_refs.objects.filter(parent_id__in=ids, child__opertype__code__in=[DETAIL_OPERS_PRD_TSK])),
                    user=request.user
                )

        return _res

    def getLoocationUsers(self, request):
        from kaf_pas.ckk.models.locations_users import Locations_users
        from isc_common.auth.managers.user_manager import UserManager

        request = DSRequest(request=request)
        data = request.get_data()

        location_sector_ids = set()
        for record in data.get('location_sector_ids'):
            for location_sector_id in record:
                location_sector_ids.add(location_sector_id)
                break

        if len(location_sector_ids) != 1:
            location_sector_ids = []
        else:
            location_sector_ids = list(location_sector_ids)

        location_id = data.get('location_id')

        parent_query = Locations_users.objects.filter(location_id__in=location_sector_ids, user=request.user)
        parent = None
        if parent_query.count() > 0:
            parent = parent_query[0]

        if parent is None:
            parent_query = Locations_users.objects.filter(location_id=location_id, user=request.user)
            if parent_query.count() > 0:
                parent = parent_query[0]

        res = [UserManager.getRecord1(item.user).get('id') for item in Locations_users.objects.filter(location_id=location_id, parent=parent)]
        res1 = [UserManager.getRecord1(item.user).get('id') for item in Locations_users.objects.filter(location_id__in=location_sector_ids)]

        res2 = list(set(res).intersection(res1))
        return [UserManager.getRecord1(User.objects.get(id=id)) for id in res2]


class Production_orderManager(CommonManager):
    production_ext = Production_ext()
    routing_ext = Routing_ext()

    @staticmethod
    def ids_list_2_opers_list(ids):
        from isc_common.models.audit import AuditModel

        if ids is None:
            return []

        ls_res = []

        if not isinstance(ids, list):
            ids = [ids]

        for id in ids:
            if isinstance(id, int):
                ls_res.append(Operations.objects.get(id=id))
            elif isinstance(id, AuditModel):
                ls_res.append(id)
            else:
                raise Exception(f'{id} must be int or Operation')
        return ls_res

    @staticmethod
    def ids_list_2_int_list(ids):
        from isc_common.models.audit import AuditModel

        if ids is None:
            return []

        if isinstance(ids, map):
            ids = list(ids)

        if not isinstance(ids, list):
            ids = [ids]

        ls_res = []
        for id in ids:
            if isinstance(id, int):
                ls_res.append(id)
            elif isinstance(id, AuditModel):
                ls_res.append(id.id)
            else:
                raise Exception(f'{id} must be int or Operation')

        return ls_res

    @staticmethod
    def refresh_all(
            ids,
            buffer_refresh=False,
            item_operations_refresh=False,
            production_order_values_refresh=False,
            production_order_opers_refresh=False,
            production_order_opers_ids=None,
            user=None,
            suffix=None
    ):
        from kaf_pas.planing.models.production_order_values import Production_order_valuesManager
        from kaf_pas.accounting.models.buffers import BuffersManager
        from kaf_pas.ckk.models.item_operations_view import Item_operations_viewManager
        from kaf_pas.planing.models.production_order_opers import Production_order_opersManager

        if ids is None:
            return

        if isinstance(ids, map):
            ids = list(ids)

        Production_order.objects.filter(id__in=Production_orderManager.ids_list_2_int_list(ids)).check_state()
        Production_orderManager.update_redundant_planing_production_order_table(ids=Production_orderManager.ids_list_2_opers_list(ids))

        if suffix is None:
            Production_orderManager.refreshRows(ids=ids, user=user)
        else:
            Production_orderManager.fullRows(suffix=suffix)

        if buffer_refresh == True:
            BuffersManager.fullRows()

        if item_operations_refresh == True:
            Item_operations_viewManager.fullRows()

        if production_order_values_refresh == True:
            Production_order_valuesManager.fullRows()

        if production_order_opers_refresh == True:
            if production_order_opers_ids is not None:
                Production_order_opersManager.refreshRows(ids=production_order_opers_ids, user=user)
            else:
                Production_order_opersManager.fullRows()

    @staticmethod
    def update_redundant_planing_production_order_table(
            ids,
            batch_mode=False,
            batch_stack=None,
    ):
        if ids is None:
            raise Exception('id must be not None')

        settings.LOCKS.acquire(settings.GRID_CONSTANTS.lock_insert_update_delete_function_of_table)

        try:
            ids = Production_orderManager.ids_list_2_opers_list(ids)

            for id in ids:
                if id.opertype != settings.OPERS_TYPES_STACK.PRODUCTION_TASK:
                    raise Exception(f'Операция: {id.opertype} не должна попадать во временные таблицы')

                if batch_mode == True and isinstance(batch_stack, Stack):
                    batch_stack.push(id.id)
                    continue

                ExecuteStoredProc('update_planing_production_order', [id.id])
                with connection.cursor() as cursor:
                    cursor.execute('''select distinct launch_id from planing_production_order_per_launch_view where id=%s''', [id.id])
                    rows = cursor.fetchall()
                    for row in rows:
                        launch_id, = row
                        ExecuteStoredProc('update_planing_production_order_per_launch', [id.id, launch_id])
                        logger.debug(f'id: {id}, launch_id: {launch_id}')

            settings.LOCKS.release(settings.GRID_CONSTANTS.lock_insert_update_delete_function_of_table)
        except Exception as ex:
            settings.LOCKS.release(settings.GRID_CONSTANTS.lock_insert_update_delete_function_of_table)
            raise ex

    @staticmethod
    def delete_redundant_planing_production_order_table(id):
        if id is None:
            raise Exception('id must be not None')

        settings.LOCKS.acquire(settings.GRID_CONSTANTS.lock_insert_update_delete_function_of_table)

        try:
            ids = Production_orderManager.ids_list_2_int_list(id)

            for id in ids:
                with connection.cursor() as cursor:
                    cursor.execute('''select distinct launch_id from planing_production_order_per_launch_view where id=%s''', [id])
                    rows = cursor.fetchall()
                    for row in rows:
                        launch_id, = row
                        res = ExecuteStoredProc('delete_planing_production_order_per_launch', [id, launch_id])
                        logger.debug(f'id: {res}')

                ExecuteStoredProc('delete_planing_production_order', [id])

            settings.LOCKS.release(settings.GRID_CONSTANTS.lock_insert_update_delete_function_of_table)
        except Exception as ex:
            settings.LOCKS.release(settings.GRID_CONSTANTS.lock_insert_update_delete_function_of_table)
            logger.error(ex)

    def updateFromRequestUpdateForwarding(self, request):
        from kaf_pas.planing.models.production_order_per_launch import Production_order_per_launch

        if not isinstance(request, DSRequest):
            request = DSRequest(request=request)

        data = request.get_data()
        executors = data.get('executors')

        idx = 0
        with transaction.atomic():
            operation_executor_stack = Operation_executor_stack()
            while True:
                _data = data.get(str(idx))
                if _data is None:
                    break
                idx += 1

                operation_id = _data.get('id')
                description = _data.get('description')

                Operations.objects.update_or_create(id=operation_id, defaults=dict(description=description))
                self.production_ext.set_executors(
                    executors=[User.objects.get(id=id) for id in executors],
                    operation=Operations.objects.get(id=operation_id),
                    user=request.user,
                    operation_executor_stack=operation_executor_stack
                )

                Production_order.objects.filter(id=operation_id).check_state()
                Production_order_per_launch.objects.filter(id=operation_id).check_state()

            for operation_executor in operation_executor_stack:
                settings.EVENT_STACK.EVENTS_PRODUCTION_ORDER_CREATE.send_message(
                    message=blinkString(f'<h4>Вам направлено: {operation_executor.qty} новых заданий на производство.</h4>', bold=True),
                    users_array=[operation_executor.executor],
                )
                Production_orderManager.fullRows(suffix=f'''_user_id_{operation_executor.executor.id}''')

        return data

    def createFromRequest(self, request):

        request = DSRequest(request=request)
        data = request.get_data()

        production_ext = Production_ext()
        production_ext.make_production_order_by_hand(data=data, user=request.user)

        return data

    def get_queryset(self):
        return Production_orderQuerySet(self.model, using=self._db)

    @staticmethod
    def refreshRows(ids, user):

        if user is None:
            return

        ids = Production_orderManager.ids_list_2_int_list(ids)
        location_ids = Production_orderQuerySet.get_user_locations(user=user)
        records = [Production_orderManager.getRecord(record=record, location_ids=location_ids) for record in Production_order.objects.filter(id__in=ids)]
        WebSocket.row_refresh_grid(grid_id=settings.GRID_CONSTANTS.refresh_production_order_grid_row, records=records)

    @staticmethod
    def fullRows(suffix=''):
        WebSocket.full_refresh_grid(grid_id=f'{settings.GRID_CONSTANTS.refresh_production_order_grid}{suffix}')

    @staticmethod
    def getRecord(record, location_ids):

        value_sum = ToDecimal(record.value_sum)
        if value_sum != 0:
            percents = round(ToDecimal(record.value_made) * 100 / ToDecimal(record.value_sum), 2)
        else:
            percents = 0

        percents_str = "%.2f" % percents
        if location_ids is not None:
            ls_set = set(location_ids)
            s_set = set(record.location_sector_ids)

            if len(s_set.intersection(ls_set)) > 0:
                status__name_arr = list(filter(lambda x: x is not None, map(lambda location_id: record.location_statuses.get(str(location_id)), location_ids)))
                status__color_arr = list(filter(lambda x: x is not None, map(lambda location_id: record.location_status_colors.get(str(location_id)), location_ids)))
                status_id_arr = list(filter(lambda x: x is not None, map(lambda location_id: record.location_status_ids.get(str(location_id)), location_ids)))

                if len(status__name_arr) > 0:
                    status__name = status__name_arr[0]
                else:
                    status__name = record.status.name

                if len(status__color_arr) > 0:
                    status__color = status__color_arr[0]
                else:
                    status__color = record.status.color

                if len(status_id_arr) > 0:
                    status_id = status_id_arr[0]
                else:
                    status_id = record.status.id
            else:
                status_id = record.status.id
                status__name = record.status.name
                status__color = record.status.color
        else:
            status_id = record.status.id
            status__name = record.status.name
            status__color = record.status.color

        if isinstance(record.value1_sum, Decimal):
            value1_sum = DecimalToStr(record.value1_sum)
            value1_sum_len = 0
        elif isinstance(record.value1_sum, list):
            value1_sum = ' / '.join([DecimalToStr(v) for v in record.value1_sum]) if record.value1_sum is not None else None
            value1_sum_len = len(record.value1_sum) if record.value1_sum is not None else None,
        else:
            value1_sum = '???'
            value1_sum_len = 0

        res = {
            'creator__short_name': record.creator.get_short_name,
            'date': record.date,
            'description': record.description,
            'demand_codes_str': record.demand_codes_str,
            'edizm__name': ' / '.join(record.edizm_arr) if record.edizm_arr is not None else None,
            'id': record.id,
            'item_id': record.item.id,
            'parent_item_id': record.parent_item.id if record.parent_item else None,
            'item__STMP_1__value_str': record.item.STMP_1.value_str if record.item.STMP_1 else None,
            'item__STMP_2__value_str': record.item.STMP_2.value_str if record.item.STMP_2 else None,
            'launch_id': record.launch.id,
            'launch__code': record.launch.code,
            'launch__date': record.launch.date,
            'location_sector_ids': Set(record.location_sector_ids).get_set_sorted_as_original,
            'location_sectors_full_name': '<br>'.join(Set(record.location_sectors_full_name).get_set_sorted_as_original),
            'num': record.num,
            'isFolder': record.isFolder,
            'cnt_opers': record.cnt_opers,
            'value_sum': DecimalToStr(record.value_sum),
            'value1_sum': value1_sum,
            'value1_sum_len': value1_sum_len,
            'value_made': DecimalToStr(record.value_made),
            'value_made_str': f'''{blinkString(DecimalToStr(record.value_made), blink=True if percents >= 100 else False, color="blue", bold=True)}({percents_str}%)''',
            'value_start': DecimalToStr(record.value_start),
            'value_odd': DecimalToStr(record.value_odd),
            'opertype__full_name': record.opertype.full_name,
            'opertype_id': record.opertype.id,
            'parent_id': record.parent.id if record.parent else None,
            'status__code': record.status.code,
            'status__name': blinkString(text=status__name, blink=False, color=status__color, bold=False),
            'status_id': status_id,
            'isDeleted': record.isDeleted,
        }
        return res

    @staticmethod
    def getRecordLevels(record):
        return dict(id=record.get('level_id'), title=record.get('level__name'))

    def makeProdOrderFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()
        setAttr(_data, 'user', request.user)

        self.routing_ext.make_routing(data=_data)
        self.production_ext.make_production_order(data=_data, batch_mode=True)
        Production_orderManager.update_redundant_planing_production_order_table(ids=self.production_ext.batch_stack.stack)
        self.production_ext.batch_stack.clear()
        WebSocket.send_info_message(
            host=settings.WS_HOST,
            port=settings.WS_PORT,
            channel=f'common_{request.user.username}',
            message='Формирование завершено.',
            logger=logger
        )
        return data

    def deleteProdOrderFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()
        setAttr(_data, 'user', request.user)
        self.production_ext.delete_production_order(data=_data)

        routing_ext = Routing_ext()
        routing_ext.clean_routing(data=_data)
        return data

    def refreshRowsProdOrderFromRequest(self, request):

        request = DSRequest(request=request)

        data = request.get_data()
        records = data.get('records')
        if isinstance(records, list):
            ids = list(map(lambda x: x.get('id'), records))

            # production_order_opers_ids = list(map(lambda x: x.child.id, Operation_refs.objects.filter(parent_id__in=ids, child__opertype__code__in=[DETAIL_OPERS_PRD_TSK])))

            Production_orderManager.update_redundant_planing_production_order_table(ids=Production_orderManager.ids_list_2_opers_list(ids))
            Production_orderManager.refreshRows(ids=ids, user=request.user)

            # Production_orderManager.refresh_all(
            #     ids=ids,
            #     production_order_opers_refresh=True,
            #     production_order_opers_ids=production_order_opers_ids,
            #     user=request.user
            # )

        return data


class Production_order(Hierarcy):
    from kaf_pas.planing.models.status_operation_types import Status_operation_types
    from kaf_pas.planing.models.operation_refs import Operation_refsManager

    arranges_exucutors = ArrayField(BigIntegerField(), default=list)
    cnt_opers = PositiveIntegerField()
    creator = ForeignKeyProtect(User, related_name='Production_order_creator')
    date = DateTimeField(default=None)
    description = TextField(null=True, blank=True)
    demand_codes_str = CodeField()
    edizm_arr = ArrayField(CodeField(null=True, blank=True), default=list)
    exucutors = ArrayField(BigIntegerField(), default=list)
    isDeleted = BooleanField()
    isFolder = BooleanField(default=None)
    item = ForeignKeyProtect(Item, related_name='Production_order_item')
    launch = ForeignKeyCascade(Launches)
    location_ids = ArrayField(BigIntegerField(), default=list)
    location_sector_ids = ArrayField(BigIntegerField(), default=list)
    location_status_ids = JSONFieldIVC()
    location_statuses = JSONFieldIVC()
    location_status_colors = JSONFieldIVC()
    location_sectors_full_name = ArrayField(TextField(), default=list)
    num = CodeField()
    opertype = ForeignKeyProtect(Operation_types, related_name='Production_order_opertype')
    parent_item = ForeignKeyProtect(Item, null=True, blank=True, related_name='Production_order_parent_item')
    props = Operation_refsManager.props()
    status = ForeignKeyProtect(Status_operation_types)
    value1_sum = ArrayField(DecimalField(decimal_places=4, max_digits=19))
    value_made = DecimalField(verbose_name='Количество  Выпущено', decimal_places=4, max_digits=19, null=True, blank=True)
    value_odd = DecimalField(verbose_name='Количество  Выпущено', decimal_places=4, max_digits=19)
    value_start = DecimalField(verbose_name='Количество Запущено', decimal_places=4, max_digits=19, null=True, blank=True)
    value_sum = DecimalField(verbose_name='Количество по документации', decimal_places=4, max_digits=19)

    objects = Production_orderManager()

    started = Status_operation_types.objects.get(code='started')

    def __str__(self):
        return f'id: {self.id}, ' \
               f'date: {DateTimeToStr(self.date)}, ' \
               f'num: {self.num}, ' \
               f'description: {self.description}, ' \
               f'opertype: [{self.opertype}], ' \
               f'creator: [{self.creator}], ' \
               f'exucutors: [{self.exucutors}], ' \
               f'status: [{self.status}], ' \
               f'launch: [{self.launch}], ' \
               f'edizm: [{self.edizm_arr}], ' \
               f'item: [{self.item}], ' \
               f'parent_item: [{self.parent_item}], ' \
               f'cnt_opers: {self.cnt_opers}, ' \
               f'value_sum: {self.value_sum},' \
               f'value1_sum: {self.value1_sum},' \
               f'value_start: {self.value_start},' \
               f'value_made: {self.value_made},' \
               f'value_odd: {self.value_odd}, ' \
               f'props: {self.props},'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Заказы на производство'
        managed = False
        # db_table = 'planing_production_order_view'
        db_table = 'planing_production_order_tbl'
