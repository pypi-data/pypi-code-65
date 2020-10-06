import logging
from datetime import datetime

from django.conf import settings
from django.db.models import Count
from events.events_manager import Event
from isc_common import Stack, setAttr, delAttr, StackElementNotExist
from isc_common.common import blinkString, uuid4, new, blue, new_man
from isc_common.datetime import StrToDate, DateToStr
from isc_common.number import compare_2_dict, Set, flen, DecimalToStr, ToDecimal
from isc_common.ws.webSocket import WebSocket

from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.planing.models.rouning_ext import Routing_ext
from kaf_pas.planing.operation_typesStack import DETAIL_OPERS_PRD_TSK
from kaf_pas.production.models.launches_ext import Launches_ext

logger = logging.getLogger(__name__)


class Operation_executor_qty:
    def __init__(self, executor, qty):
        self.executor = executor
        self.qty = qty

    def __str__(self):
        return f'executor : {self.executor}, qty: {self.qty}'


class Operation_executor_stack(Stack):
    len = 0

    def push(self, item, exists_function=None, logger=None):
        from isc_common.auth.models.user import User
        if not isinstance(item.executor, User):
            raise Exception('executor mast be User instance')

        try:
            executor_qty = self.find_one(lambda _item: _item.executor == item.executor)
            executor_qty.qty += item.qty
            self.len += item.qty

            if logger is not None:
                logger.debug(f'operation_executor_qty: {executor_qty}')

        except StackElementNotExist:
            operation_executor_qty = Operation_executor_qty(executor=item.executor, qty=item.qty)
            if logger is not None:
                logger.debug(f'operation_executor_qty: {operation_executor_qty}')

            super().push(Operation_executor_qty(executor=item.executor, qty=item.qty))
            self.len += 1


class OperationEvent(Event):
    def send_message(self, message=None, users_array=None, progress=None, _len=None):
        from isc_common.auth.models.user import User
        if isinstance(users_array, User):
            users_array = [users_array]
        super().send_message(message=message, users_array=users_array, progress=progress)

    def send_message1(self, operation_executor_stack: Operation_executor_stack, progress=None):
        for operation_executor_messages in operation_executor_stack.stack:
            for message in operation_executor_messages.messages.stack:
                super().send_message(message=message, users_array=[operation_executor_messages.executor], progress=progress)


class Operation_executor_messages:
    def __init__(self, executor, message):
        self.executor = executor
        self.messages = Stack([message])


class OperationPlanItem:
    item_id = None
    launch_ids = None
    sum = None
    value = None

    # Определить цех ресурса
    def get_resource_workshop(self, operation_resources):
        from kaf_pas.ckk.models.locations import Locations
        from django.conf import settings

        res_set = set()
        for operation_resource in operation_resources:
            for location in Locations.objects_tree.get_parents(id=operation_resource.location.id, child_id='id', include_self=False):
                if location.props.isWorkshop == True:
                    res, _ = settings.OPERS_STACK.NOT_UNDEFINED_WORKSHOP(location)
                    res_set.add(res.location.id)

        if len(res_set) == 0:
            raise Exception('Не обнаружен цех, с признаком "Уровень цеха"')
        lst = list(res_set)
        return list(Locations.objects.filter(id__in=lst))

    def get_locations_users_query(self, locations):
        from kaf_pas.ckk.models.locations_users import Locations_users
        from isc_common.common import blinkString

        res_set = set()
        for location in locations:
            locations_users_query = Locations_users.objects.filter(location=location, parent=None, props=Locations_users.props.resiver_production_order)
            if locations_users_query.count() == 0:
                raise Exception(blinkString(text=f'Не обнаружен ответственный исполнитель для : {location.full_name}', bold=True))

            for locations_users in locations_users_query:
                res_set.add(locations_users.id)

        res = list(Locations_users.objects.filter(id__in=list(res_set)))
        return res

    def __init__(self, *args, **kwargs):
        # from kaf_pas.ckk.models.item import Item
        from kaf_pas.production.models.resource import Resource
        from kaf_pas.production.models.operations_item import Operations_item
        from kaf_pas.production.models.operation_resources import Operation_resources
        from kaf_pas.production.models.operation_material import Operation_material
        from django.db import connection
        from django.conf import settings
        from kaf_pas.ckk.models.item import Item

        class OperationsItem:
            def __init__(self, operation_item):
                operation_resources = Operation_resources.objects.get(operationitem=operation_item)
                self.operation_item = operation_item
                self.operation_resource = operation_resources
                self.ed_izm = operation_item.ed_izm
                self.num = operation_item.num
                self.operation = operation_item.operation
                self.color = operation_item.color
                self.old_num = operation_item.old_num
                self.qty = operation_item.qty

                self.location_fin = operation_resources.location_fin

                self.resource = operation_resources.resource
                if self.resource is None:
                    self.resource, _ = Resource.objects.get_or_create(location=self.operation_resource.location, code='none')

                self.resource_fin = operation_resources.resource_fin
                if self.resource_fin is None and self.operation_resource.location_fin is not None:
                    self.resource_fin, _ = Resource.objects.get_or_create(location=self.operation_resource.location_fin, code='none')

                self.operation_materials = Stack([operation_material for operation_material in Operation_material.objects.filter(operationitem=operation_item)])

            def __str__(self):
                return f'''\n\noperation_item: [\n\n{self.operation_item}] \n operation_resource: [{self.operation_resource}] \n operation_materials: [[{", ".join([operation_material for operation_material in self.operation_materials])}]]'''

        class LaunchSumValue:
            sum = None

            def __init__(self, sum_value, sum_value1, edizm_id, launch_id, item_id):
                from kaf_pas.production.models.launches import Launches

                self.sum_value = sum_value
                self.sum_value1 = sum_value1
                self.edizm_id = edizm_id
                self.item_id = item_id
                self.launch = Launches.objects.get(id=launch_id)

            def __str__(self):
                return f'sum: {self.sum}, launch: [{self.launch}]'

        class LaunchSumValues(Stack):
            def __init__(self, item, launch_ids):
                super().__init__()

                self.stack = []
                with connection.cursor() as cursor:
                    sql_str = '''select sum(distinct pov.value),
                                           sum(distinct pov1.value),
                                           pol.launch_id,
                                           pov.edizm_id
                                   from planing_operation_launches as pol
                                             join planing_operations as po on po.id = pol.operation_id
                                             join planing_operation_item as poit on po.id = poit.operation_id
                                             join planing_operation_value pov on pov.operation_id = po.id
                                             join planing_operation_value pov1 on pov1.operation_id = po.id
                                   where pol.launch_id in %s
                                      and po.opertype_id = %s
                                      and poit.item_id = %s
                                      and is_bit_on(pov.props::integer, 0) = false
                                      and is_bit_on(pov1.props::integer, 0) = true
                                    group by pol.launch_id, pov.edizm_id'''

                    cursor.execute(sql_str, [launch_ids, settings.OPERS_TYPES_STACK.ROUTING_TASK.id, item.id])
                    rows = cursor.fetchall()

                    for row in rows:
                        sum_value, sum_value1, launch_id, edizm_id = row
                        launchSumValue = LaunchSumValue(sum_value=sum_value, sum_value1=sum_value1, edizm_id=edizm_id, launch_id=launch_id, item_id=item.id)
                        self.push(launchSumValue)

            def __str__(self):
                return '\n\n'.join([f'[{elem}]' for elem in self.stack])

        if len(kwargs) == 0:
            raise Exception(f'{self.__class__.__name__} kwargs is empty')

        for k, v in kwargs.items():
            setattr(self, k, v() if callable(v) else v)

        if isinstance(self.item_id, int):
            self.item = Item.objects.get(id=self.item_id)

        if self.item is None:
            raise Exception('self.item not determined')

        self.operations_item = Stack([OperationsItem(operation_item) for operation_item in Operations_item.objects.filter(item=self.item).exclude(deleted_at__isnull=False).order_by('num')])

        self.resources_location_fin_arr = [(operation_item.resource, operation_item.resource_fin, operation_item.location_fin) for operation_item in self.operations_item]

        # operation_item = self.operations_item.stack[0].operation_item
        oit_lst = [a.operation_item for a in self.operations_item]
        operation_resources = [operation_resources for operation_resources in Operation_resources.objects.filter(operationitem__in=oit_lst)]
        top_locations = self.get_resource_workshop(operation_resources=operation_resources)

        self.locations_users = [location_user for location_user in self.get_locations_users_query(locations=top_locations)]

        self.launchSumValues = LaunchSumValues(item=self.item, launch_ids=self.launch_ids)

    def __str__(self):
        # return f'item: {self.item} \n value_sum: {self.value}\n value_per_one: {self.value1}\n\n launchSumValues: [\n{self.launchSumValues.stack}\n] \n\n operations_item: [\n{", ".join([f"[{elem}]" for elem in self.operations_item])}]'
        return f'item: {self.item} \n value_sum: {self.value}\n  launchSumValues: [\n{self.launchSumValues.stack}\n] \n\n operations_item: [\n{", ".join([f"[{elem}]" for elem in self.operations_item])}]'


class Production_ext:
    routing_ext = Routing_ext()
    _res = []

    batch_mode = False
    batch_stack = Stack()
    edizm_shtuka = Ed_izm.objects.get(code='шт')

    def start(self, qty, _data, user, operation_executor_stack, lock=True):
        from django.conf import settings
        from django.db import connection
        from django.forms import model_to_dict
        from isc_common.auth.models.user import User
        from isc_common.common import new
        from isc_common.common import restarted
        from isc_common.common.functions import ExecuteStoredProc
        from kaf_pas.planing.models.operation_item import Operation_item
        from kaf_pas.planing.models.operation_launches import Operation_launches
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.models.operation_value import Operation_value
        from kaf_pas.planing.models.operations import Operations
        from kaf_pas.planing.models.operations_view import Operations_view
        from kaf_pas.planing.models.production_order import Production_orderManager
        from kaf_pas.planing.models.production_order_per_launch import Production_order_per_launch
        from kaf_pas.production.models.launches import Launches

        key = f'''get_setStartStatus_{_data.get('id')}'''
        if lock:
            settings.LOCKS.acquire(key)
        try:
            value_made = ExecuteStoredProc('get_value_made', [_data.get('id'), _data.get('launch_id')])

            if value_made > qty:
                if lock:
                    settings.LOCKS.release(key)
                raise Exception('Количество выпуска больше введенной суммы. Введите с учетом выпущенного.')

            parent = Operations.objects.get(id=_data.get('id'))
            item = Operation_item.objects.get(operation=parent).item
            launch = Launches.objects.get(id=_data.get('launch_id'))

            if Production_order_per_launch.objects.filter(id=parent.id).count() > 1:
                if lock:
                    settings.LOCKS.release(key)
                raise Exception(f'{item.item_name} входит в несколько запусков, поэтому ввести данные по запуску из {launch.code} невозможно.')

            operation_refs = Operation_refs.objects.filter(
                parent=parent,
                child__opertype_id=settings.OPERS_TYPES_STACK.LAUNCH_TASK.id
            )

            if operation_refs.count() > 0:
                if qty == 0:
                    Operation_value.objects.filter(operation=operation_refs[0].child).delete()
                    Operation_launches.objects.filter(operation=operation_refs[0].child).delete()
                    parent.status = settings.OPERS_TYPES_STACK.PRODUCTION_TASK_STATUSES.get(new)
                    operation_refs.delete()

                else:
                    Operation_value.objects.update_or_create(operation=operation_refs[0].child, defaults=dict(value=qty))
                    Operation_launches.objects.get_or_create(
                        operation=operation_refs[0].child,
                        launch=Operations_view.objects.get(id=operation_refs[0].child.id).launch
                    )
                    parent.status = settings.OPERS_TYPES_STACK.PRODUCTION_TASK_STATUSES.get(restarted)

                parent.creator = user
                parent.save()

                if qty != 0:
                    res = model_to_dict(operation_refs[0].parent)
                    # _data.update(res)
                    self._res.append(_data)
                setAttr(_data, 'value_start', qty)

            else:
                if qty == 0:
                    if lock:
                        settings.LOCKS.release(key)
                    return self._res

                res = Operations.objects.create(
                    opertype=settings.OPERS_TYPES_STACK.LAUNCH_TASK,
                    date=datetime.now(),
                    status=settings.OPERS_TYPES_STACK.LAUNCH_TASK_STATUSES.get(new),
                    creator=user
                )

                # parent = Operations.objects.get(id=_data.get('id'))
                parent.status = settings.OPERS_TYPES_STACK.PRODUCTION_TASK_STATUSES.get('started')
                parent.creator = user
                parent.save()

                Production_orderManager.update_redundant_planing_production_order_table(parent)

                Operation_refs.objects.create(parent=parent, child=res)
                edizm_id = _data.get('edizm_id')
                if edizm_id is None:
                    edizm_id = self.edizm_shtuka.id

                Operation_value.objects.create(operation=res, edizm_id=edizm_id, value=qty)
                Operation_launches.objects.get_or_create(operation=res, launch=launch if launch.parent is None else launch.parent)

                with connection.cursor() as cursor:
                    cursor.execute('''select distinct clu.user_id
                                        from planing_production_order_opers_view poop
                                                 join ckk_locations_users clu on clu.location_id = poop.location_id
                                        where poop.parent_id = %s
                                          and poop.production_operation_id not in (select operation_id from production_operation_executor)
                                        union
                                        select distinct prdex.user_id
                                        from planing_production_order_opers_view poop
                                                 join production_operation_executor prdex on prdex.operation_id = poop.production_operation_id
                                        where poop.parent_id = %s''', [parent.id, parent.id])
                    rows = cursor.fetchall()

                    self.set_executors(
                        executors=list(User.objects.filter(id__in=[row for row, in rows]).distinct()),
                        operation=parent,
                        operation_executor_stack=operation_executor_stack,
                        user=user,
                        send=False
                    )

                # res = model_to_dict(res)
                # _data.update(res)

                setAttr(_data, 'value_start', qty)
                self._res.append(_data)

            Production_orderManager.refresh_all(
                ids=parent,
                production_order_opers_refresh=True,
                user=user
            )

            if lock:
                settings.LOCKS.release(key)

            return self._res
        except Exception as ex:
            self._res.clear()
            if lock:
                settings.LOCKS.release(key)
            raise ex

    def set_executors(self, executors, operation, operation_executor_stack, user, send=True):
        from kaf_pas.planing.models.operation_executor import Operation_executor

        cnt = 0
        if isinstance(executors, list):
            # Раннее назначенные исполнителя для данной операции
            for executor in executors:
                operation_executor, created = Operation_executor.objects.get_or_create(operation=operation, executor=executor)

                if user != executor:
                    operation_executor_stack.push(
                        Operation_executor_qty(executor=operation_executor.executor, qty=1),
                        logger
                    )
                cnt += 1

        # От лица запускающего операцию ртправляем
        if cnt > 0 and send:
            try:
                operation_executor = Operation_executor.objects.get(operation=operation, executor=user)
                operation_executor.props |= Operation_executor.props.rearrange
                operation_executor.save()

                from kaf_pas.planing.models.production_order import Production_orderManager
                Production_orderManager.update_redundant_planing_production_order_table(operation.id)
            except Operation_executor.DoesNotExist:
                pass

    def rec_operation(self,
                      description,
                      item,
                      operation,
                      launch,
                      operation_item,
                      opertype,
                      status,
                      user,
                      props=0,
                      ):
        from datetime import datetime
        from kaf_pas.ckk.models.item import Item
        from kaf_pas.planing.models.operation_item import Operation_item
        from kaf_pas.planing.models.operation_launches import Operation_launches
        from kaf_pas.planing.models.operation_material import Operation_material
        from kaf_pas.planing.models.operation_operation import Operation_operation
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.models.operation_resources import Operation_resources
        from kaf_pas.planing.models.operations import Operations
        from kaf_pas.production.models.launches import Launches

        if isinstance(launch, int):
            launch = Launches.objects.get(id=launch)

        if isinstance(item, int):
            item = Item.objects.get(id=item)

        if isinstance(operation, int):
            operation = Operations.objects.get(id=operation)

        production_order_operation_opers = Operations.objects.create(
            date=datetime.now(),
            opertype=opertype,
            status=status,
            creator=user,
            description=description,
            editing=False,
            deliting=False
        )

        operation_launches = Operation_launches.objects.create(
            operation=production_order_operation_opers,
            launch=launch
        )
        logger.debug(f'Created operation_launches :  {operation_launches}')

        if operation_item.resource is not None:
            operation_resources = Operation_resources.objects.create(
                operation=production_order_operation_opers,
                resource=operation_item.resource,
                resource_fin=operation_item.resource_fin,
                location_fin=operation_item.location_fin
            )
            logger.debug(f'Created operation_resources :  {operation_resources}')

        for operation_material in operation_item.operation_materials:
            operation_material = Operation_material.objects.create(
                operation=production_order_operation_opers,
                material=operation_material.material,
                material_askon=operation_material.material_askon,
                edizm=operation_material.edizm,
                qty=operation_material.qty,
            )
            logger.debug(f'Created operation_material :  {operation_material}')

        operation_operation = Operation_operation.objects.create(
            operation=production_order_operation_opers,
            production_operation=operation_item.operation,
            color=operation_item.color,

            ed_izm=operation_item.ed_izm,
            num=operation_item.num,
            qty=operation_item.qty,
            creator=user,
            props=props
        )
        logger.debug(f'Created operation_operation :  {operation_operation}')

        operation_item, created = Operation_item.objects.get_or_create(
            operation=production_order_operation_opers,
            item=item,
        )
        if created:
            logger.debug(f'Created operation_item :  {operation_item}')

        operation_refs = Operation_refs.objects.create(
            parent=operation,
            child=production_order_operation_opers,
            props=Operation_refs.props.product_order_routing,
        )
        logger.debug(f'Created operation_refs :  {operation_refs}')

        return production_order_operation_opers

    def rec_operations(self, launch, status, operationPlanItem, operation, opertype, description, user):

        for operation_item in operationPlanItem.operations_item:
            self.rec_operation(
                launch=launch,
                status=status,
                operation_item=operation_item,
                item=operationPlanItem.item,
                operation=operation,
                opertype=opertype,
                description=description,
                user=user
            )

    def rec_item(self,
                 item_id,
                 launch_childs_ids,
                 launch_parent,
                 user,
                 operation_executor_stack,
                 route_opers_lunch,
                 description,
                 status_name=new
                 ):
        from datetime import datetime
        from django.conf import settings
        from kaf_pas.planing.models.operation_executor import Operation_executor
        from kaf_pas.planing.models.operation_item import Operation_item
        from kaf_pas.planing.models.operation_launches import Operation_launches
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.models.operation_resources import Operation_resources
        from kaf_pas.planing.models.operation_value import Operation_value
        from kaf_pas.planing.models.operations import Operations
        from kaf_pas.planing.models.production_order import Production_order
        from kaf_pas.planing.models.production_order import Production_orderManager
        from kaf_pas.planing.models.production_order_per_launch import Production_order_per_launch

        route_oparation_item = dict(
            item_id=item_id,
            launch_ids=launch_childs_ids,
            launch_parent_id=launch_parent.id
        )

        operationPlanItem = OperationPlanItem(**route_oparation_item)

        # Головная операция заказа
        production_order_operation = Operations.objects.create(
            date=datetime.now(),
            opertype=settings.OPERS_TYPES_STACK.PRODUCTION_TASK,
            status=settings.OPERS_TYPES_STACK.PRODUCTION_TASK_STATUSES.get(status_name),
            description=description,
            creator=user,
            editing=False,
            deliting=False
        )
        logger.debug(f'Created operation :  {production_order_operation}')

        operation_launches = Operation_launches.objects.create(
            operation=production_order_operation,
            launch=launch_parent
        )
        logger.debug(f'Created operation_launches :  {operation_launches}')

        operation_item = Operation_item.objects.create(
            operation=production_order_operation,
            item=operationPlanItem.item,
        )
        logger.debug(f'Created operation_item :  {operation_item}')

        for launch_child_id in launch_childs_ids:
            for route_oper_lunch in route_opers_lunch:
                if route_oper_lunch[1] == launch_child_id:
                    for item_id in route_oper_lunch[0]:
                        operation_refs = Operation_refs.objects.create(
                            child=production_order_operation,
                            parent_id=item_id,
                            props=Operation_refs.props.product_order_routing,
                        )
                        logger.debug(f'Created operation_refs :  {operation_refs}')

        for resources_location_fin in operationPlanItem.resources_location_fin_arr:
            operation_resources, created = Operation_resources.objects.get_or_create(
                operation=production_order_operation,
                resource=resources_location_fin[0],
                resource_fin=resources_location_fin[1],
                location_fin=resources_location_fin[2]
            )
            if created:
                logger.debug(f'Created operation_resources :  {operation_resources}')

        for launchSumValue in operationPlanItem.launchSumValues.stack:
            production_order_operation_launch = Operations.objects.create(
                date=datetime.now(),
                opertype=settings.OPERS_TYPES_STACK.PRODUCTION_DETAIL_SUM_TASK,
                status=settings.OPERS_TYPES_STACK.PRODUCTION_DETAIL_SUM_TASK_STATUSES.get(new),
                creator=user,
                editing=False,
                deliting=False
            )
            logger.debug(f'Created operation :  {production_order_operation}')

            # todo Ищем запущенную товарную позицию
            # self.check_exists_in_production(items=[Item.objects.get(id=item_id)])

            operation_launches = Operation_launches.objects.create(
                operation=production_order_operation_launch,
                launch=launchSumValue.launch
            )
            logger.debug(f'Created operation_launches :  {operation_launches}')

            operation_value = Operation_value.objects.create(
                operation=production_order_operation_launch,
                edizm_id=launchSumValue.edizm_id,
                value=launchSumValue.sum_value
            )
            logger.debug(f'Created operation_value :  {operation_value}')

            operation_value = Operation_value.objects.create(
                operation=production_order_operation_launch,
                edizm_id=launchSumValue.edizm_id,
                value=launchSumValue.sum_value1,
                props=Operation_value.props.perone
            )
            logger.debug(f'Created operation_value :  {operation_value}')

            operation_refs = Operation_refs.objects.create(
                child=production_order_operation_launch,
                parent=production_order_operation,
                props=Operation_refs.props.product_order_routing,
            )
            logger.debug(f'Created operation_refs :  {operation_refs}')

        self.rec_operations(
            launch=launch_parent,
            status=settings.OPERS_TYPES_STACK.PRODUCTION_DETAIL_OPERS_TASK_STATUSES.get(new),
            operationPlanItem=operationPlanItem,
            operation=production_order_operation,
            opertype=settings.OPERS_TYPES_STACK.PRODUCTION_DETAIL_OPERS_TASK,
            description=description,
            user=user
        )

        for location_user in operationPlanItem.locations_users:
            operation_executor, created = Operation_executor.objects.get_or_create(
                operation=production_order_operation,
                executor=location_user.user,
            )
            if created:
                logger.debug(f'Created operation_executor :  {operation_executor}')

            operation_executor_stack.push(
                Operation_executor_qty(executor=location_user.user, qty=1),
                logger
            )

        Production_order.objects.filter(id=production_order_operation.id).check_state()
        Production_order_per_launch.objects.filter(id=production_order_operation.id).check_state()
        Production_orderManager.update_redundant_planing_production_order_table(
            production_order_operation,
            batch_mode=self.batch_mode,
            batch_stack=self.batch_stack,
        )

    def make_production_order(self, data, batch_mode=False):
        from django.conf import settings
        from django.db import transaction
        from isc_common.bit import TurnBitOn
        from isc_common.common import blinkString
        from isc_common.datetime import DateToStr
        from isc_common.progress import managed_progress
        from isc_common.progress import progress_deleted
        from isc_common.progress import ProgressDroped
        from kaf_pas.production.models.launches import Launches
        from kaf_pas.production.models.launches_view import Launches_viewManager
        from kaf_pas.planing.models.production_order import Production_orderManager

        self.batch_mode = batch_mode
        self.batch_stack.clear()

        user = data.get('user')

        if isinstance(user, int):
            from isc_common.auth.models.user import User
            user = User.objects.get(id=user)

        class Launch_pair:
            def __init__(self, child, parent):
                if isinstance(child, int):
                    self.child = Launches.objects.get(id=child)
                elif isinstance(child, Launches):
                    self.child = child
                else:
                    raise Exception('child must be int or Launches')

                if isinstance(parent, int):
                    self.parent = Launches.objects.get(id=parent)
                elif isinstance(parent, Launches):
                    self.parent = parent
                else:
                    raise Exception('parent must be int or Launches')

            def __str(self):
                return f'child: [{self.child}], parent: [{self.parent}]'

        class Launch_pairs(Stack):
            def get_parents(self):
                res = set()
                for item in self.stack:
                    for item1 in item:
                        res.add(item1.parent)

                return list(res)

            def get_parent_ids(self):
                return [item.id for item in self.get_parents()]

            def get_childs(self, parent):
                res = set()
                for item in self.stack:
                    res1 = [i.child for i in item if i.parent == parent and i.child.status != settings.PROD_OPERS_STACK.IN_PRODUCTION]
                    for r in res1:
                        res.add(r)
                return list(res)

            def get_child_ids(self, parent):
                return [item.id for item in self.get_childs(parent=parent)]

        launch_pairs = Launch_pairs()

        launches_head = []
        for launch_id in set(data.get('data')):
            _launch = Launches.objects.get(id=launch_id)
            if _launch.parent is None:
                launches = list(Launches.objects.filter(parent=_launch))
            else:
                launches = [_launch]

            launch_pairs.push([Launch_pair(parent=launch.parent, child=launch) for launch in launches])
            if _launch.parent is None:
                launches_head.append(_launch)
            else:
                launches_head.append(_launch.parent)

        for launch_parent in launch_pairs.get_parents():
            if launch_parent.code != '000':
                if launch_parent.status == settings.PROD_OPERS_STACK.IN_PRODUCTION:
                    continue

            key = f'OperationsManager.make_production_order_{launch_parent.id}'
            settings.LOCKS.acquire(key)

            launch_childs = launch_pairs.get_childs(parent=launch_parent)
            launch_childs_ids = tuple([launch.id for launch in launch_childs])

            operation_executor_stack = Operation_executor_stack()

            sql_items = '''select poit.item_id
                                 from planing_operation_item as poit
                                   join planing_operation_launches as pol on poit.operation_id = pol.operation_id
                                   join planing_operations as po on po.id = pol.operation_id
                                 where pol.launch_id in %s
                                   and po.opertype_id = %s
                                 group by poit.item_id'''

            sql_items_launch = '''select array_agg(poit_det.operation_id)
                                       from planing_operation_item as poit_det
                                                join planing_operation_launches as pol on poit_det.operation_id = pol.operation_id
                                                join planing_operations as po on po.id = pol.operation_id
                                       where pol.launch_id = %s
                                         and po.opertype_id = %s
                                         and poit_det.item_id = %s
                                       group by pol.launch_id'''

            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(f'''select count(*) from ({sql_items}) as s''', [launch_childs_ids, settings.OPERS_TYPES_STACK.ROUTING_TASK.id])
                qty, = cursor.fetchone()
                logger.debug(f'qty: {qty}')

                message = [f'<h3>Создание заданий на производство ({qty} товарных позиций) <p/>']

                message.extend([blinkString(f'Запуск № {launch.code} от {DateToStr(launch.date)}', blink=False, bold=True, color='blue') for launch in launch_childs])
                message = '<br/>'.join(message)

                with managed_progress(
                        id=f'order_by_prod_launch_{launch_parent.id}_{user.id}',
                        qty=qty,
                        user=user,
                        message=message,
                        title='Выполнено',
                        props=TurnBitOn(0, 0)
                ) as progress:

                    with transaction.atomic():
                        def except_func():
                            settings.LOCKS.release(key)

                        progress.except_func = except_func

                        cursor.execute(sql_items, [launch_childs_ids, settings.OPERS_TYPES_STACK.ROUTING_TASK.id])
                        rows = cursor.fetchall()
                        for row in rows:
                            item_id, = row

                            # items_4_find = ItemManager.find_item(item_id)

                            route_opers_lunch = []
                            for launch_childs_id in launch_childs_ids:
                                cursor.execute(sql_items_launch, [launch_childs_id, settings.OPERS_TYPES_STACK.ROUTING_TASK.id, item_id])
                                rows_lunch = cursor.fetchall()
                                for row_lunch in rows_lunch:
                                    row_lunch, = row_lunch
                                    route_opers_lunch.append((row_lunch, launch_childs_id))

                            self.rec_item(
                                item_id=item_id,
                                launch_childs_ids=launch_childs_ids,
                                launch_parent=launch_parent,
                                user=user,
                                operation_executor_stack=operation_executor_stack,
                                route_opers_lunch=route_opers_lunch,
                                description=data.get('description'),
                                status_name=new if launch_parent.code != '000' else new_man
                            )

                            if progress.step() != 0:
                                Launches_viewManager.fullRows()
                                settings.LOCKS.release(key)
                                raise ProgressDroped(progress_deleted)

                            Launches_viewManager.refreshRows(ids=launch_parent.id)
                            Launches_viewManager.refreshRows(ids=launch_childs_ids)

                        launch_parent.status = settings.PROD_OPERS_STACK.IN_PRODUCTION
                        launch_parent.save()

                        for launch_child in launch_childs:
                            launch_child.status = settings.PROD_OPERS_STACK.IN_PRODUCTION
                            launch_child.save()

                            Launches_viewManager.refreshRows(ids=launch_child.id)

                        settings.LOCKS.release(key)

                    logger.debug(f'operation_executor_stack.len: {operation_executor_stack.len} messages')
                    for operation_executor in operation_executor_stack:
                        settings.EVENT_STACK.EVENTS_PRODUCTION_ORDER_CREATE.send_message(
                            message=blinkString(f'<h4>Вам направлено: {operation_executor.qty} новых заданий на производство.</h4>', bold=True),
                            users_array=[operation_executor.executor],
                            progress=progress,
                        )

        records = launch_pairs.get_parent_ids()
        for parent in launch_pairs.get_parent_ids():
            records.extend([_id for _id in launch_pairs.get_child_ids(parent=parent)])

        Launches_viewManager.refreshRows(ids=records)
        Production_orderManager.fullRows()

    def delete_production_order(self, data):
        from django.conf import settings
        from django.db import transaction
        from isc_common.bit import TurnBitOn
        from isc_common.common import blinkString
        from isc_common.datetime import DateToStr
        from isc_common.progress import managed_progress
        from isc_common.progress import progress_deleted
        from isc_common.progress import ProgressDroped
        from kaf_pas.planing.models.operation_executor import Operation_executor
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.production.models.launches import Launches
        from kaf_pas.production.models.launches_view import Launches_viewManager
        from kaf_pas.planing.models.production_order_values_ext import Production_order_values_ext
        from kaf_pas.planing.models.production_order import Production_orderManager
        from kaf_pas.planing.models.operation_launches import Operation_launches
        from kaf_pas.planing.models.operation_operation import Operation_operation
        from kaf_pas.accounting.models.buffers import BuffersManager
        from isc_common.auth.models.user import User

        user = data.get('user')

        launch_ids = data.get('data')
        if not isinstance(launch_ids, list):
            raise Exception('launch_ids must be list')

        launch_ids = list(set(launch_ids))
        production_order_values_ext = Production_order_values_ext()

        if isinstance(user, int):
            user = User.objects.get(id=user)
        elif not isinstance(user, User):
            raise Exception('user must be int or User')

        operation_executor_stack = Operation_executor_stack()

        launch_cnt = len(launch_ids)
        idx = 0
        operation_launch_deleted = 0
        parent_launch_ids = []

        for parent_launch_id in launch_ids:
            parent_launch = Launches.objects.get(id=parent_launch_id)
            if parent_launch.parent is None:
                parent_launch_ids.append(parent_launch.id)

            key = f'OperationsManager.delete_production_order_{parent_launch.id}'
            settings.LOCKS.acquire(key)
            # print(model_to_dict(parent_launch))

            if parent_launch.parent is None:
                child_launches = [launch.id for launch in Launches.objects.filter(parent=parent_launch)]
            else:
                child_launches = [parent_launch]

            operations_launch = Operation_launches.objects.filter(
                operation__opertype=settings.OPERS_TYPES_STACK.PRODUCTION_TASK,
                launch=parent_launch
            )

            operations_launch_cnt = operations_launch.count()
            logger.debug(f'operations_launch.count() = {operations_launch_cnt}')

            with managed_progress(
                    id=f'delete_order_by_prod_launch_{parent_launch.id}_{user.id}',
                    qty=operations_launch_cnt,
                    user=user,
                    message=f'<h3>Удаление заданий на производство, Запуск № {parent_launch.code} от {DateToStr(parent_launch.date)}</h3>',
                    title='Выполнено',
                    props=TurnBitOn(0, 0)
            ) as progress:
                def except_func():
                    settings.LOCKS.release(key)

                progress.except_func = except_func

                with transaction.atomic():
                    for operation_launch in operations_launch:

                        # Операции сумм разбивки по запускам/ заказам на продажу
                        operation_refs_sums = Operation_refs.objects.filter(
                            parent=operation_launch.operation,
                            child__opertype=settings.OPERS_TYPES_STACK.PRODUCTION_DETAIL_SUM_TASK
                        )
                        logger.debug(f'Операции сумм разбивки по запускам/ заказам на продажу: {operation_refs_sums.count()}')

                        for operation_refs_sum in operation_refs_sums:
                            operation_sum = operation_refs_sum.child

                            deleted = operation_refs_sum.delete()
                            logger.debug(f'deleted: {deleted}')

                            deleted = operation_sum.delete()
                            logger.debug(f'deleted: {deleted}')

                        # Техннологические операции
                        operation_refs_sums_dets = Operation_refs.objects.filter(
                            parent=operation_launch.operation,
                            child__opertype=settings.OPERS_TYPES_STACK.PRODUCTION_DETAIL_OPERS_TASK)

                        for operation_refs_sums_det in operation_refs_sums_dets:
                            logger.debug(f'Технологические операции: {operation_refs_sums_dets.count()}')

                            operations_operation = Operation_operation.objects.filter(operation=operation_refs_sums_det.child).order_by('-num')

                            for operation_operation in operations_operation:
                                # Выполнение по этим технологическим операциям
                                maked_values = Operation_refs.objects.filter(
                                    parent=operation_operation.operation,
                                    child__opertype=settings.OPERS_TYPES_STACK.MADE_OPERATIONS_PLS_TASK
                                ).order_by('-child_id')

                                maked_values = [o.child for o in maked_values]

                                logger.debug(f'Выполнение по ({operation_operation.num}) : {len(maked_values)}')
                                if len(maked_values) > 0:
                                    def func_refreshed():
                                        Launches_viewManager.refreshRows(ids=parent_launch.id)
                                        Launches_viewManager.refreshRows(ids=child_launches)
                                        BuffersManager.fullRows()

                                    production_order_values_ext.delete_sums(operations=maked_values, func_refreshed=func_refreshed, parent=data)

                                deleted = Operation_refs.objects.filter(parent=operation_launch.operation, child=operation_operation.operation).delete()
                                logger.debug(f'deleted: {deleted}')

                                deleted = Operation_refs.objects.filter(parent__isnull=True, child=operation_operation.operation).delete()
                                logger.debug(f'deleted: {deleted}')

                                deleted = Operation_refs.objects.filter(parent__opertype__in=[settings.OPERS_TYPES_STACK.ROUTING_TASK], child=operation_operation.operation).delete()
                                logger.debug(f'deleted: {deleted}')

                                deleted = operation_operation.operation.delete()
                                logger.debug(f'deleted: {deleted}')

                            operation_det = operation_refs_sums_det.child
                            deleted = operation_refs_sums_det.delete()
                            logger.debug(f'deleted: {deleted}')

                            deleted = operation_det.delete()
                            logger.debug(f'deleted: {deleted}')

                        operation_executors = Operation_executor.objects.filter(operation=operation_launch.operation, props=Operation_executor.props.relevant)

                        for operation_executor in operation_executors:
                            operation_executor_stack.push(
                                item=Operation_executor_qty(executor=operation_executor.executor, qty=1),
                                logger=logger
                            )

                        deleted = Operation_refs.objects.filter(parent__isnull=True, child=operation_launch.operation).delete()
                        logger.debug(f'deleted: {deleted}')

                        deleted = Operation_refs.objects.filter(parent__opertype=settings.OPERS_TYPES_STACK.ROUTING_TASK, child=operation_launch.operation).delete()
                        logger.debug(f'deleted: {deleted}')

                        for operation_refs_launch in Operation_refs.objects.filter(parent=operation_launch.operation, child__opertype__in=[
                            settings.OPERS_TYPES_STACK.LAUNCH_TASK,
                        ]):
                            deleted = Operation_refs.objects.filter(parent__opertype=settings.OPERS_TYPES_STACK.PRODUCTION_TASK, child=operation_refs_launch.child).delete()
                            logger.debug(f'deleted: {deleted}')

                            _operation_refs_launch = operation_refs_launch.child

                            deleted = operation_refs_launch.delete()
                            logger.debug(f'deleted: {deleted}')

                            deleted = _operation_refs_launch.delete()
                            logger.debug(f'deleted: {deleted}')

                        deleted = operation_launch.operation.delete()

                        operation_launch_deleted += deleted[0]
                        logger.debug(f'deleted: {deleted}')

                        Launches_viewManager.refreshRows(ids=parent_launch.id)
                        if isinstance(child_launches, list) and len(child_launches) > 0:
                            ids = Production_orderManager.ids_list_2_int_list(child_launches)
                            Launches_viewManager.refreshRows(ids=ids)

                        if progress.step() != 0:
                            Launches_viewManager.fullRows()
                            settings.LOCKS.release(key)
                            raise ProgressDroped(progress_deleted)

                    for launch in Launches.objects.filter(parent=parent_launch):
                        # print(model_to_dict(launch))
                        launch.status = settings.PROD_OPERS_STACK.ROUTMADE
                        launch.save()

                        Launches_viewManager.refreshRows(ids=launch.id)

                    idx += 1
                    if idx == launch_cnt:
                        parent_launch.status = settings.PROD_OPERS_STACK.ROUTMADE
                        parent_launch.save()

                        Launches_viewManager.refreshRows(ids=parent_launch.id)
                        # progress.setContentsLabel('Обновление предстваления planing_production_order_mview')

                logger.debug(f'operation_executor_stack.len: {operation_executor_stack.len} сообщений')
                for operation_executor in operation_executor_stack:
                    settings.EVENT_STACK.EVENTS_PRODUCTION_ORDER_CREATE.send_message(
                        message=blinkString(f'<h4>Удалиено: {operation_executor.qty} заданий на производство.</h4>', bold=True),
                        users_array=[operation_executor.executor],
                        progress=progress,
                    )

            settings.LOCKS.release(key)
            return idx

        if operation_launch_deleted > 0:
            Production_orderManager.fullRows()
            BuffersManager.fullRows()

    def get_production_order_tmp_table(self, id, tmp_table_name=None):
        from isc_common.common.mat_views import create_tmp_table

        if tmp_table_name is None:
            tmp_table_name = f'''tmp_{uuid4()}'''

        create_tmp_table(
            on_commit=None,
            drop=False,
            sql_str='''SELECT distinct t.*
                                       FROM planing_operations po
                                                join planing_operation_item poi on po.id = poi.operation_id
                                                join planing_operation_item_add paoi on poi.item_id = paoi.item_id
                                                CROSS JOIN LATERAL
                                           json_to_recordset(paoi.item_full_name_obj::json) as t(
                                                                                                "confirmed" text,
                                                                                                "deliting" boolean,
                                                                                                "document__file_document" text,
                                                                                                "document_id" bigint,
                                                                                                "editing" boolean,
                                                                                                "id" bigint,
                                                                                                "isFolder" boolean,
                                                                                                "lastmodified" text,
                                                                                                "parent_id" bigint,
                                                                                                "props" bigint,
                                                                                                "qty_operations" int4,
                                                                                                "refs_id" bigint,
                                                                                                "refs_props" bigint,
                                                                                                "relevant" text,
                                                                                                "section" text,
                                                                                                "STMP_1_id" bigint,
                                                                                                "STMP_2_id" bigint,
                                                                                                "version" int4,
                                                                                                "where_from" text
                                           )
                                       where po.id = %s''',
            params=[id],
            table_name=tmp_table_name)
        return tmp_table_name

    def _create_tech_specification(self, data, old_data, key):
        from kaf_pas.production.models.operation_def_material import Operation_def_material
        from kaf_pas.production.models.operation_material import Operation_material
        from kaf_pas.production.models.operation_resources import Operation_resources
        from kaf_pas.production.models.operations_item import Operations_item

        created, updated, renumered, deleted = self.is_changed_data(data=data, old_data=old_data)
        logger.debug(f'is_changed_data: (created: {created}, updated: {updated}, renumered: {renumered}, deleted: {deleted})')

        if not created:
            return

        operations_item, created = Operations_item.objects.update_or_create(
            item=data.parentRecord.item,
            operation=data.production_operation,
            defaults=dict(
                description=data.description,
                ed_izm=data.production_operation_edizm,
                num=data.production_operation_num,
                props=Operations_item.props.created,
                qty=data.production_operation_qty,
            )
        )

        if not created:
            old_data = data
            operations_item.soft_restore()
            operations_item.props |= Operations_item.props.created
            operations_item.save()
            data.operation_item = operations_item
            logger.debug(f'\noperations_item: {operations_item}\n')

        operation_resources, created = Operation_resources.objects.update_or_create(
            operationitem=operations_item,
            defaults=dict(
                batch_size=1,
                location=data.location,
                location_fin=data.location_fin,
                resource=data.resource,
                resource_fin=data.resource_fin,
            )
        )
        if not created:
            operation_resources.soft_restore()
            logger.debug(f'\noperation_resources: {operation_resources}\n')

        for operation_def_material in Operation_def_material.objects.filter(operation_id=data.production_operation_id):
            operation_material, created = Operation_material.objects.update_or_create(
                operationitem=operations_item,
                defaults=dict(
                    material=operation_def_material.material,
                    material_askon=operation_def_material.material_askon,
                    edizm=operation_def_material.edizm,
                    qty=operation_def_material.qty)
            )

            if not created:
                operation_material.soft_restore()
                logger.debug(f'\noperation_material: {operation_material}\n')
        return old_data

    def insert_update_item(self, insert_item, bb, data):
        if len(bb) + 1 <= data.production_operation_num:
            bb.append(insert_item)
            insert_item.num = len(bb)
            insert_item.save()
        else:
            bb.insert(data.production_operation_num - 1, insert_item)
        return bb

    def _update_tech_specification(self, data, old_data, key):
        from kaf_pas.production.models.operation_resources import Operation_resources
        from kaf_pas.production.models.operations_item import Operations_item
        from kaf_pas.planing.models.operation_item import Operation_item
        from kaf_pas.planing.models.operation_operation import Operation_operation

        created, updated, renumered, deleted = self.is_changed_data(data=data, old_data=old_data)
        logger.debug(f'is_changed_data: (created: {created}, updated: {updated}, renumered: {renumered}, deleted: {deleted})')

        if not updated and not created and not deleted:
            return

        if deleted:
            data = old_data

        # Опреция задания на производство
        if data.parentRecord is not None:
            parent_operation_item = Operation_item.objects.get(operation=data.parentRecord.this)
        elif data.parent is not None:
            parent_operation_item = Operation_item.objects.get(operation=data.parent)
        else:
            raise Exception('Не найден parentRecord')

        if created:
            renumered = True
            aa = list(Operations_item.objects.filter(item=parent_operation_item.item, props=Operations_item.props.created).alive())
            if len(aa) > 1:
                raise Exception('Количество вставляемых операций может быть = 1')
            else:
                if len(aa) == 0:
                    aa = [data.operation_item]

                insert_item = aa[0]

                bb = list(Operations_item.objects.filter(item=parent_operation_item.item).alive().exclude(id__in=map(lambda x: x.id, aa)).order_by('num'))
                bb = self.insert_update_item(insert_item=insert_item, bb=bb, data=data)

        elif updated:
            if not renumered:
                renumered = flen(filter(lambda x: x.get('cnt') > 1, Operations_item.objects.filter(item=parent_operation_item.item).order_by('num').values('num').annotate(cnt=Count('num')))) > 0

            if renumered:
                aa = list(Operations_item.objects.filter(item=parent_operation_item.item, num=old_data.production_operation_num).alive())
                if len(aa) != 1:
                    raise Exception('Количество изменяемых операций может быть = 1')
                insert_item = aa[0]

                bb = list(Operations_item.objects.filter(item=parent_operation_item.item).alive().exclude(num=old_data.production_operation_num).order_by('num'))

                bb = self.insert_update_item(insert_item=insert_item, bb=bb, data=data)

            else:
                bb = Operations_item.objects.filter(item=parent_operation_item.item).alive().order_by('num')
        elif deleted:
            renumered = True
            operations = map(lambda x: x.operation, Operation_item.objects.filter(item=parent_operation_item.item, operation__deleted_at__isnull=False))
            prod_operations = map(lambda x: x.production_operation, Operation_operation.objects.filter(operation__in=operations))
            deleting_operations = Operations_item.objects.filter(item=parent_operation_item.item, operation__in=prod_operations)
            for deleting_operation in deleting_operations:
                deleted = deleting_operation.soft_delete()
                logger.debug(f'\ndeleted: {deleted}\n')

            bb = Operations_item.objects.filter(item=parent_operation_item.item).alive().order_by('num')
        else:
            raise Exception('Unknown type')

        if renumered:
            num = 1
            for updatedItem in bb:
                if updatedItem.num != num:
                    updatedItem.old_num = updatedItem.num
                    updatedItem.num = num
                    updatedItem.save()
                num += 1

        if updated:
            operations_item = bb[data.production_operation_num - 1]
            operations_item.qty = data.production_operation_qty
            operations_item.color = data.production_operation_color
            operations_item.ed_izm = data.production_operation_edizm
            operations_item.description = data.description
            operations_item.save()

            for operation_resources in Operation_resources.objects.filter(operationitem=operations_item):
                # Данные по ресурсам и местоположениям данной операции
                operation_resources.location = data.location
                operation_resources.resource = data.resource
                operation_resources.resource_fin = data.resource_fin
                operation_resources.location_fin = data.location_fin
                operation_resources.save()
        pass

    def _update_prod_specifications_mat_res(self, launch_operations_item, operation_item, key):
        from kaf_pas.production.models.operation_resources import Operation_resources
        from kaf_pas.production.models.launch_operation_resources import Launch_operation_resources
        from kaf_pas.production.models.launch_operation_material import Launch_operations_material
        from kaf_pas.production.models.operation_material import Operation_material
        # Изменяем ресурсы согласно технологической спецификации
        for operation_resource in Operation_resources.objects.filter(operationitem=operation_item):

            for launch_operation_resources in Launch_operation_resources.objects.filter(operation_resources=operation_resource, launch_operationitem=launch_operations_item):
                if operation_resource.resource is not None:
                    launch_operation_resources.resource = operation_resource.resource

                if operation_resource.resource_fin is not None:
                    launch_operation_resources.resource_fin = operation_resource.resource_fin

                launch_operation_resources.location = operation_resource.location
                launch_operation_resources.location_fin = operation_resource.location_fin
                launch_operation_resources.batch_size = operation_resource.batch_size
                launch_operation_resources.save()

        # Изменяем материалы согласно технологической спецификации
        for operation_material in Operation_material.objects.filter(operationitem=operation_item):
            for launch_operation_material in Launch_operations_material.objects.filter(operation_material=operation_material, launch_operationitem=launch_operations_item):
                launch_operation_material.edizm = operation_material.edizm
                launch_operation_material.material = operation_material.material
                launch_operation_material.material_askon = operation_material.material_askon
                launch_operation_material.qty = operation_material.qty
                launch_operation_material.save()

    def _update_prod_specifications(self, data, old_data, user, key):
        from django.conf import settings
        from kaf_pas.planing.models.operation_launch_item import Operation_launch_item
        from kaf_pas.planing.models.operation_operation import Operation_operation
        from kaf_pas.production.models.launch_operation_material import Launch_operations_material
        from kaf_pas.production.models.launch_operation_resources import Launch_operation_resources
        from kaf_pas.production.models.launch_operations_item import Launch_operations_item
        from kaf_pas.production.models.operation_material import Operation_material
        from kaf_pas.production.models.operations_item import Operations_item
        from kaf_pas.production.models.operation_resources import Operation_resources
        from kaf_pas.production.models.launches import Launches

        created, updated, renumered, deleted = self.is_changed_data(data=data, old_data=old_data)
        logger.debug(f'is_changed_data: (created: {created}, updated: {updated}, renumered: {renumered}, deleted: {deleted})')

        if not updated and not created and not deleted:
            return

        if deleted:
            data = old_data

        if data.parentRecord is not None:
            parentRecord = data.parentRecord
        elif data.parent is not None:
            parentRecord = data.parent
        else:
            raise Exception('Не найден parentRecord')

        if parentRecord.launch.parent is not None:
            launches = [parentRecord.launch]
        else:
            launches = parentRecord.launch.child_launches

        launch_operations_items_stack = Stack()

        if deleted:
            # Удаляем операции не входящие в технологическую спецификацию
            for launch_operations_item in Launch_operations_item.objects. \
                    filter(launch__in=launches). \
                    filter(operationitem_id__in=list(map(lambda x: x.id, Operations_item.objects.filter(item=parentRecord.item, deleted_at__isnull=False)))). \
                    alive(). \
                    exclude(launch__status=settings.PROD_OPERS_STACK.CLOSED):

                launch_operation_resources = Launch_operation_resources.objects.filter(launch_operationitem=launch_operations_item).soft_delete()
                if launch_operation_resources is not None:
                    logger.debug(f'\nLaunch_operation_resources deleted: {launch_operation_resources}\n')

                launch_operations_material = Launch_operations_material.objects.filter(launch_operationitem=launch_operations_item).soft_delete()
                if launch_operations_material is not None:
                    logger.debug(f'\nLaunch_operations_material deleted: {launch_operations_material}\n')

                launch_operations_item_deleted = launch_operations_item.soft_delete()
                if launch_operations_item_deleted is not None:
                    launch_operations_items_stack.push(launch_operations_item)
                    logger.debug(f'\nlaunch_operations_item deleted: {launch_operations_item_deleted}\n')

        # Изменяем операции согласно изменений технологической спецификации
        if updated:
            for operation_item in Operations_item.objects.filter(item=parentRecord.item).order_by('num'):
                for launch in launches:
                    for launch_operations_item in Launch_operations_item.objects.filter(item=operation_item.item, launch=launch, operation=operation_item.operation):

                        if launch_operations_item.operationitem == operation_item:
                            pass

                        if launch_operations_item.launch.status == settings.PROD_OPERS_STACK.CLOSED:
                            continue

                        # launch_operations_item.description = 'Обновлено'
                        launch_operations_item.ed_izm = operation_item.ed_izm
                        launch_operations_item.color = operation_item.color
                        launch_operations_item.num = operation_item.num
                        launch_operations_item.old_num = operation_item.old_num
                        launch_operations_item.qty = operation_item.qty
                        launch_operations_item.props = Launch_operations_item.props.updated
                        launch_operations_item.deleted_at = operation_item.deleted_at
                        launch_operations_item.save()

                        launch_operations_items_stack.push(launch_operations_item)
                        logger.debug(f'\nlaunch_operations_item: {launch_operations_item}\n')

                        # Изменяем ресурсы согласно технологической спецификации
                        self._update_prod_specifications_mat_res(
                            launch_operations_item=launch_operations_item,
                            operation_item=operation_item,
                            key=key
                        )

        elif deleted:
            for operation_item in Operations_item.objects.filter(item=parentRecord.item, deleted_at__isnull=False):
                # for launch_operations_item in Launch_operations_item.objects.filter(item=operation_item.item, launch__in=launches):
                #     launch_operations_item.soft_delete()

                for _launch_operations_item in Launch_operations_item.objects.filter(item=operation_item.item, launch__in=launches).alive():
                    for _operations_item in Operations_item.objects.filter(item=operation_item.item, operation=_launch_operations_item.operation):
                        if _launch_operations_item.num != _operations_item.num:
                            _launch_operations_item.num = _operations_item.num
                            _launch_operations_item.save()

        elif created:
            created_operation_items = Operations_item.objects.filter(item=parentRecord.item, props=Operations_item.props.created).order_by('num')
            for operation_item in created_operation_items:
                launches = Launch_operations_item.objects.filter(item=operation_item.item, launch__in=launches).values('launch').distinct()
                for launch_dict in launches:
                    launch_operations_item, created = Launch_operations_item.objects.update_or_create(
                        item=operation_item.item,
                        launch=Launches.objects.get(id=launch_dict.get('launch')),
                        operation=operation_item.operation,
                        operationitem=operation_item,
                        color=operation_item.color,
                        defaults=dict(
                            description=data.description,
                            ed_izm=operation_item.ed_izm,
                            num=operation_item.num,
                            old_num=operation_item.old_num,
                            props=operation_item.props.created,
                            qty=operation_item.qty,
                        )
                    )

                    if not created:
                        if launch_operations_item.is_deleted:
                            launch_operations_item.soft_restore()
                            launch_operations_items_stack.push(launch_operations_item)
                            created = True
                    else:
                        launch_operations_items_stack.push(launch_operations_item)

                    if created:
                        try:
                            operation_resources = Operation_resources.objects.get(operationitem=operation_item)

                            launch_operation_resources, created = Launch_operation_resources.objects.update_or_create(
                                launch_operationitem=launch_operations_item,
                                defaults=dict(
                                    batch_size=operation_resources.batch_size,
                                    location=operation_resources.location,
                                    location_fin=operation_resources.location_fin,
                                    operation_resources=operation_resources,
                                    resource=operation_resources.resource if operation_resources.resource else operation_resources.location.resource,
                                    resource_fin=operation_resources.resource_fin,
                                )
                            )
                            logger.debug(f'\nlaunch_operation_resources.resource: {launch_operation_resources}\n')

                            if not created:
                                launch_operation_resources.soft_restore()

                            launch_operations_item.resource = launch_operation_resources.resource
                            launch_operations_item.resource_fin = launch_operation_resources.resource_fin
                            launch_operations_item.location_fin = launch_operation_resources.location_fin
                        except Operation_resources.DoesNotExist:
                            raise Exception('Resource not found')

                        logger.debug(f'\nlaunch_operations_item.resource: {launch_operations_item.resource}\n')
                        logger.debug(f'\nlaunch_operations_item.location_fin: {launch_operations_item.location_fin}\n')

                        launch_operations_item.operation_materials = Stack()
                        for operation_material in Operation_material.objects.filter(operationitem=operation_item):
                            launch_operations_material, created = Launch_operations_material.objects.update_or_create(
                                launch_operationitem=launch_operations_item,
                                defaults=dict(
                                    edizm=operation_material.edizm,
                                    material=operation_material.material,
                                    material_askon=operation_material.material_askon,
                                    operation_material=operation_material,
                                    qty=operation_material.qty
                                )
                            )

                            if not launch_operations_material:
                                launch_operations_material.soft_restore()

                            logger.debug(f'\nlaunch_operations_material: {launch_operations_material}\n')
                            launch_operations_item.operation_materials.push(operation_material)

                        logger.debug(f'\nlaunch_operations_item.operation_materials: {launch_operations_item.operation_materials}\n')

                        try:
                            operation_launch_item = Operation_launch_item.objects.get(
                                launch_item=launch_operations_item,
                                operation__opertype=settings.OPERS_TYPES_STACK.ROUTING_TASK
                            )
                            logger.debug(f'\noperation_launch_item: {operation_launch_item}\n')

                        except Operation_launch_item.DoesNotExist:
                            operation = self.rec_operation(
                                description=data.description,
                                item=parentRecord.item,
                                launch=parentRecord.launch,
                                operation=parentRecord.this,
                                operation_item=launch_operations_item,
                                opertype=settings.OPERS_TYPES_STACK.ROUTING_TASK,
                                props=Operation_operation.props.direct_created,
                                status=settings.OPERS_TYPES_STACK.ROUTING_TASK_STATUSES.get(new),
                                user=user,
                            )
                            logger.debug(f'\noperation: {operation}\n')

                            operation_launch_item = Operation_launch_item.objects.create(
                                operation=operation,
                                launch_item=launch_operations_item
                            )
                            logger.debug(f'\noperation_launch_item: {operation_launch_item}\n')

                for _launch_operations_item in Launch_operations_item.objects.filter(item=operation_item.item, launch__in=launches).alive().order_by('num', '-lastmodified'):
                    _operations_item = Operations_item.objects.get(id=_launch_operations_item.operationitem.id)
                    if _launch_operations_item.num != _operations_item.num:
                        _launch_operations_item.num = _operations_item.num
                        _launch_operations_item.save()

                operation_item.props &= ~ Operations_item.props.created
                operation_item.save()

        return launch_operations_items_stack

    def _update_routing(self, data, old_data, updated_launch_operations_items: Stack, user, key):

        created, updated, renumered, deleted = self.is_changed_data(data=data, old_data=old_data)
        logger.debug(f'is_changed_data: (created: {created}, updated: {updated}, renumered: {renumered}, deleted: {deleted})')

        if not renumered and not created and not deleted:
            return

        if deleted:
            data = old_data

        self.routing_ext.update_routing(data=data, old_data=old_data, updated_launch_operations_items=updated_launch_operations_items, user=user, key=key)

    def _created_production_orders(self, data, old_data, user, updated_launch_operations_items, key):
        from django.conf import settings
        from kaf_pas.planing.models.operation_launch_item import Operation_launch_item
        from kaf_pas.planing.models.operation_operation import Operation_operation
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.models.production_order_opers import Production_order_opers
        from kaf_pas.planing.models.production_order_values_ext import Production_orderWrapper
        from kaf_pas.production.models.launch_operation_material import Launch_operations_material
        from kaf_pas.production.models.launch_operation_resources import Launch_operation_resources
        from kaf_pas.production.models.launch_operations_item import Launch_operations_item

        if old_data is not None:
            parent = data.parent
            if parent is None:
                parent = data.parentRecord.this

            operations = list(map(lambda x: x.child, Operation_refs.objects.filter(parent=parent, child__opertype__code=DETAIL_OPERS_PRD_TSK)))
            if len(operations) == 0:
                old_data = None

        created, updated, renumered, deleted = self.is_changed_data(data=data, old_data=old_data)

        if not created:
            return

        logger.debug(f'is_changed_data: (created: {created}, updated: {updated}, renumered: {renumered}, deleted: {deleted})')

        opers_stack = Set()
        for created_launch_operations_item in updated_launch_operations_items:
            _continue = False

            for if_deleted_operation in data.parentRecord.all_childs.filter(production_operation=created_launch_operations_item.operation):
                if if_deleted_operation.is_deleted:
                    for operation_refs in Operation_refs.objects.filter(child_id=if_deleted_operation.id, parent_id=if_deleted_operation.parent_id):
                        for operation_operation in Operation_operation.objects.filter(operation=operation_refs.child):
                            deleted = operation_operation.operation.soft_restore()
                            _continue = deleted is not None

            if _continue:
                continue

            if opers_stack.is_exists(created_launch_operations_item.operation.id):
                continue

            operation_launch_item = list(map(lambda x: x.launch_item, Operation_launch_item.objects.filter(
                launch_item=created_launch_operations_item,
                # operation__opertype__code__in=[DETAIL_OPERS_PRD_TSK]
            ).distinct()))
            logger.debug(f'\noperation_launch_item: {operation_launch_item}')

            operation_resources = Launch_operation_resources.objects.filter(launch_operationitem__in=operation_launch_item)
            operation_materials = list(Launch_operations_material.objects.filter(launch_operationitem__in=operation_launch_item))

            if operation_resources.count() == 0:
                raise Exception('Not found resource')
            if operation_resources.count() > 1:
                raise Exception('Resources must be == 1')
            operation_resources = operation_resources[0]
            logger.debug(f'\noperation_resources: {operation_resources}')

            operationitem = Production_orderWrapper(
                color=created_launch_operations_item.color,
                ed_izm=created_launch_operations_item.ed_izm,
                location_fin=operation_resources.location_fin,
                num=created_launch_operations_item.num,
                operation=created_launch_operations_item.operation,
                operation_materials=operation_materials,
                qty=created_launch_operations_item.qty,
                resource=operation_resources.resource,
                resource_fin=operation_resources.resource_fin,
            )

            if data.parentRecord.launch.parent is None:
                launch = data.parentRecord.launch
            else:
                launch = data.parentRecord.launch.parent

            operation_det = self.rec_operation(
                description=data.description,
                item=data.parentRecord.item,
                launch=launch,
                operation=data.parentRecord.this,
                operation_item=operationitem,
                opertype=settings.OPERS_TYPES_STACK.PRODUCTION_DETAIL_OPERS_TASK,
                props=Operation_operation.props.direct_created,
                status=settings.OPERS_TYPES_STACK.PRODUCTION_DETAIL_OPERS_TASK_STATUSES.get(new),
                user=user,
            )

            # Проверить наличие операций у соседей
            production_order_opers = Production_order_opers.objects.get(id=operation_det.id)
            if production_order_opers.right_neighbour is not None and production_order_opers.right_neighbour.has_moving_operations:
                raise Exception(f'Операцию вставить или нельзя, у следующей операции уже было движение позиций.')

            operations = list(map(lambda x: x.child, Operation_refs.objects.filter(parent=data.parentRecord.this, child__opertype__code=DETAIL_OPERS_PRD_TSK)))
            operations_operation = list(Operation_operation.objects.filter(operation__in=operations).order_by('num'))

            if data.parentRecord.launch.parent is not None:
                launches = [data.parentRecord.launch]
            else:
                launches = data.parentRecord.launch.child_launches

            launch_operations_items = None
            for launch in launches:
                launch_operations_items = Launch_operations_item.objects.filter(launch=launch, item=data.parentRecord.item).alive().order_by('num')
                if len(launch_operations_items) == len(operations):
                    break

            if launch_operations_items is None:
                raise Exception(f'Production spec not found')

            for operation_operation in operations_operation:
                for production_operation in filter(lambda x: x.operation.id == operation_operation.production_operation.id, launch_operations_items):
                    if production_operation.num != operation_operation.num:
                        operation_operation.num = production_operation.num
                        operation_operation.save()

        return old_data

    def _update_production_orders(self, data, old_data, user, updated_launch_operations_items, key):
        from kaf_pas.planing.models.operation_operation import Operation_operation
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.models.operation_resources import Operation_resources
        from kaf_pas.production.models.launch_operation_resources import Launch_operation_resources
        from kaf_pas.planing.operation_typesStack import DETAIL_OPERS_PRD_TSK
        from kaf_pas.production.models.launch_operations_item import Launch_operations_item

        created, updated, renumered, deleted = self.is_changed_data(data=data, old_data=old_data)
        logger.debug(f'is_changed_data: (created: {created}, updated: {updated}, renumered: {renumered}, deleted: {deleted})')

        if not updated and not deleted:
            return

        if deleted:
            data = old_data

        operations = list(map(lambda x: x.child, Operation_refs.objects.filter(parent=data.parent, child__opertype__code=DETAIL_OPERS_PRD_TSK)))
        operations_operation = Operation_operation.objects.filter(operation__in=operations).order_by('num')

        for updated_launch_operations_item in updated_launch_operations_items:
            try:
                if updated:
                    for operation_operation in operations_operation.filter(production_operation=updated_launch_operations_item.operation):
                        logger.debug(f'operation_operation: {operation_operation}')
                        operation_operation.soft_restore()

                        operation_resources = Operation_resources.objects.get(operation=operation_operation.operation, deleted_at=None)
                        logger.debug(f'\n------operation_resources: {operation_resources}')
                        launch_operation_resources = Launch_operation_resources.objects.get(launch_operationitem=updated_launch_operations_item)
                        logger.debug(f'\n------launch_operation_resources: {launch_operation_resources}')

                        operation_resources.location_fin = launch_operation_resources.location_fin
                        operation_resources.resource = launch_operation_resources.resource
                        operation_resources.resource_fin = launch_operation_resources.resource_fin
                        operation_resources.save()
                        logger.debug(f'operation_resources: {operation_resources}')

                        operation_operation.production_operation = updated_launch_operations_item.operation
                        operation_operation.ed_izm = updated_launch_operations_item.ed_izm
                        operation_operation.color = updated_launch_operations_item.color

                        if operation_operation.num != updated_launch_operations_item.num:
                            operation_operation.num = updated_launch_operations_item.num
                            operation_operation.old_num = updated_launch_operations_item.old_num
                            # self._re_arrange_neighbour()

                        operation_operation.color = updated_launch_operations_item.color
                        operation_operation.qty = updated_launch_operations_item.qty
                        operation_operation.deleted_at = updated_launch_operations_item.deleted_at
                        operation_operation.save()

                elif deleted:
                    if updated_launch_operations_item.is_deleted:
                        for operation_operation in Operation_operation.objects.filter(
                                operation__in=operations,
                                production_operation=updated_launch_operations_item.operation
                        ):
                            # self._re_arrange_neighbour()
                            operation_operation.soft_delete()
            except Operation_operation.DoesNotExist:
                pass

        if deleted:
            for operation_operation in Operation_operation.objects.filter(operation__in=operations).alive().order_by('num'):
                for launch_operations_item in Launch_operations_item.objects.filter(
                        item=data.parent.item,
                        launch=data.launch if data.launch.parent is not None else data.launch.child_launches[0],
                        operation=operation_operation.production_operation,
                ).alive():
                    if operation_operation.num != launch_operations_item.num:
                        operation_operation.num = launch_operations_item.num
                        operation_operation.save()

    def is_changed_data(self, data, old_data):
        if data is None:
            return False, False, False, True

        if old_data is None:
            return True, False, False, False

        if data.resource != old_data.resource:
            data.resource.location = old_data.resource.location
            return False, True, False, False

        if data.resource_fin != old_data.resource_fin:
            data.resource_fin.location = old_data.resource_fin.location
            return False, True, False, False

        if data.location != old_data.location:
            data.resource = data.location.resource
            return False, True, False, False

        if data.location_fin != old_data.location_fin:
            data.resource_fin = data.location_fin.resource
            return False, True, False, False

        if data.production_operation_num != old_data.production_operation_num:
            # if data.this.opertype == settings.OPERS_TYPES_STACK.PRODUCTION_TASK:
            #     if flen(data.this.minus_values) > 0:
            #         raise Exception(f'Выполнение невозможно, есть связанные выпуски.')
            return False, True, True, False

        if data.production_operation_qty != old_data.production_operation_qty:
            return False, True, False, False

        if data.production_operation_edizm_id != old_data.production_operation_edizm_id:
            return False, True, False, False

        if data.production_operation_id != old_data.production_operation_id:
            return False, True, False, False

        if data.description != old_data.description:
            return False, True, False, False

        if data.color != old_data.color:
            return False, True, False, False

        if data.production_operation_color_id != old_data.production_operation_color_id:
            return False, True, False, False

        return False, True, False, False

    def _refreshed_operations_view(self, data, old_data, user):
        from kaf_pas.planing.models.production_order_opers import Production_order_opersManager
        from kaf_pas.planing.models.production_order import Production_orderManager

        created, updated, renumered, deleted = self.is_changed_data(data=data, old_data=old_data)
        logger.debug(f'is_changed_data: (created: {created}, updated: {updated}, renumered: {renumered}, deleted: {deleted})')
        if not created and not updated and not renumered and not deleted:
            return

        if deleted:
            parent_id = old_data.parent.id
        elif created:
            parent_id = data.parentRecord.this.id
        elif updated:
            parent_id = data.parent.id
        else:
            raise Exception('parent Not Found')

        # Production_orderManager.update_redundant_planing_production_order_table(ids=parent_id)

        if updated and old_data is not None and not renumered:
            # Production_order_opersManager.refreshRows(ids=data.id, user=user)
            Production_order_opersManager.fullRows(suffix=f'''_{parent_id}''')
        elif created or renumered or deleted:
            Production_order_opersManager.fullRows(suffix=f'''_{parent_id}''')

        Production_orderManager.refreshRows(parent_id, user=user)

    def _delete_tech_specification(self, id, key, user):
        from kaf_pas.planing.models.operations import Operations
        from kaf_pas.planing.models.production_order_opers import Production_order_opers
        from kaf_pas.planing.models.production_order_opers import Production_order_opersManager
        from kaf_pas.planing.models.production_order_values_ext import Production_orderWrapper

        production_order_opers = Production_order_opers.objects.get(id=id)
        if production_order_opers.has_moving_operations:
            raise Exception(f'Операцию удалить нельзя, уже было движение позиций.')

        operation = Operations.objects.get(id=production_order_opers.id)
        operation.soft_delete()

        data = None

        old_data = Production_order_opersManager.getRecord(record=Production_order_opers.objects.get(id=id), user=user)
        logger.debug(f'old_data: {old_data}')

        old_data = Production_orderWrapper(**old_data)

        # Меняем порядок строк операций в технологической спецификации с учетом удаленной
        self._update_tech_specification(data=data, old_data=old_data, key=key)

        # Меняем порядок строк операций вв производственных спецификациях с учетом удаленной
        updated_launch_operations_items = self._update_prod_specifications(data=data, old_data=old_data, user=user, key=key)

        # Корректируем маршрутизацию согласно порядку следования операций
        # self._update_routing(data=data, old_data=old_data, updated_launch_operations_items=updated_launch_operations_items, user=user, key=key)

        # Коректируем делаизацию заказа на производсво, в плане операций
        self._update_production_orders(updated_launch_operations_items=updated_launch_operations_items, data=data, old_data=old_data, user=user, key=key)

        # Обновляем грид операций
        self._refreshed_operations_view(data=data, old_data=old_data, user=user)

    def update_operation(self, data, user, old_data=None):
        from django.conf import settings
        from django.db import transaction
        from kaf_pas.planing.models.production_order_opers import Production_order_opers
        from kaf_pas.planing.models.production_order_opers import Production_order_opersManager
        from kaf_pas.production.models.operation_def_resources import Operation_def_resources
        from kaf_pas.planing.models.production_order_values_ext import Production_orderWrapper

        logger.debug(f'data={data}')
        logger.debug(f'old_data={old_data}')

        if data is not None:
            if data.get('location_id') is None and data.get('resource_id') is None:
                try:
                    operation_def_resources = Operation_def_resources.objects.get(operation_id=data.get('production_operation_id'))
                    setAttr(data, 'location_id', operation_def_resources.location.id if operation_def_resources.location else None)
                    setAttr(data, 'location_fin_id', operation_def_resources.location_fin.id if operation_def_resources.location_fin else None)
                    setAttr(data, 'resource_id', operation_def_resources.resource.id if operation_def_resources.resource else None)
                    setAttr(data, 'resource_fin_id', operation_def_resources.resource_fin.id if operation_def_resources.resource_fin else None)

                except Operation_def_resources.DoesNotExist:
                    raise Exception('Не определен ресурс или местоположение.')

        with transaction.atomic():
            key = f'''update_operation_{data.get('id')}''' if data.get('id') is not None else None
            try:
                if key is not None:
                    settings.LOCKS.acquire(key)

                    if data.get('id') is not None:
                        try:
                            production_order_opers = Production_order_opers.objects.get(id=data.get('id'))
                            if data is not None and old_data is not None:
                                if data.get('production_operation_num') != old_data.get('production_operation_num'):
                                    if production_order_opers.has_moving_operations:
                                        raise Exception(f'Операцию переместить нельзя нельзя, уже было движение позиций.')

                            check_data = Production_order_opersManager.getRecord(record=production_order_opers, user=user)

                            delAttr(old_data, 'date')
                            delAttr(old_data, 'value_made')
                            delAttr(old_data, 'value_start')
                            delAttr(old_data, 'value_odd')
                            delAttr(old_data, 'value_odd_ship')
                            delAttr(old_data, 'edizm__name')
                            delAttr(old_data, 'launch_id')

                            delAttr(check_data, 'date')
                            delAttr(check_data, 'value_made')
                            delAttr(check_data, 'value_odd')
                            delAttr(check_data, 'value_odd_ship')
                            delAttr(check_data, 'value_start')
                            delAttr(check_data, 'edizm__name')
                            delAttr(check_data, 'launch_id')

                            messages = compare_2_dict(old_data, check_data)
                            if len(messages) > 0:
                                Production_order_opersManager.refreshRows(ids=check_data.get('id'), user=user)
                                settings.LOCKS.release(key)
                                messages_str = '\n'.join(messages)
                                raise Exception(f'''<pre>'Данные операции изменились, повторите выполнение, \n'{messages_str}</pre>''')
                        except Production_order_opers.DoesNotExist:
                            Production_order_opersManager.fullRows()
                            settings.LOCKS.release(key)
                            raise Exception('''Операция уже удалена''')

                data = Production_orderWrapper(**data)
                old_data = Production_orderWrapper(**old_data) if old_data is not None else None

                # Cоздаем новую операцию
                old_data = self._create_tech_specification(data=data, old_data=old_data, key=key)

                # Меняем строку операции в технологической спецификации
                self._update_tech_specification(data=data, old_data=old_data, key=key)

                # Меняем строки операций в производственных спецификациях, которые относятся к запуску из data получаем список измененных строк
                updated_launch_operations_items = self._update_prod_specifications(data=data, user=user, old_data=old_data, key=key)

                # Корректируем маршрутизацию согласно порядку следования операций
                # self._update_routing(data=data, old_data=old_data, updated_launch_operations_items=updated_launch_operations_items, user=user, key=key)

                # Создаем новую операцию в детаизации заказа на производсво, в плане операций
                old_data = self._created_production_orders(updated_launch_operations_items=updated_launch_operations_items, data=data, old_data=old_data, user=user, key=key)

                # Коректируем делаизацию заказа на производсво, в плане операций
                self._update_production_orders(updated_launch_operations_items=updated_launch_operations_items, data=data, old_data=old_data, user=user, key=key)

                # Обновляем грид операций
                self._refreshed_operations_view(data=data, old_data=old_data, user=user)

                if key is not None:
                    settings.LOCKS.release(key)
            except Exception as ex:
                if key is not None:
                    settings.LOCKS.release(key)
                raise ex

            # raise NotImplement()
        return data

    def delete_operation(self, ids, user):
        from django.conf import settings
        from django.db import transaction
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.operation_typesStack import DETAIL_OPERS_PRD_TSK

        if isinstance(ids, int):
            ids = [ids]

        with transaction.atomic():
            childs = Operation_refs.objects.filter(
                parent__in=map(lambda x: x.parent, Operation_refs.objects.filter(child_id__in=ids)),
                child__opertype__code__in=[DETAIL_OPERS_PRD_TSK],
                child__deleted_at=None
            )

            if childs.count() == len(ids):
                raise Exception('Удалить все операции нельзя.')

            for id in ids:
                logger.debug(f'id: {id}')
                key = f'''delete_operation_{id}'''
                settings.LOCKS.acquire(key)

                try:
                    self._delete_tech_specification(id=id, key=key, user=user)

                    settings.LOCKS.release(key)
                except Exception as ex:
                    settings.LOCKS.release(key)
                    raise ex

            # raise NotImplement()

    def check_exists_in_production(self, qty, user, items=None, item=None, launch__date=None, callbackData=None):
        from kaf_pas.ckk.models.item import ItemManager
        from kaf_pas.planing.models.production_order_opers_per_launch import Production_order_opers_per_launch

        # Ищем по совпадению обозначения и наименования, для этого сначала ищем все похожие обозначения и наименования
        if items is None:
            items = ItemManager.find_item(item)

        value = 0
        for production_order in Production_order_opers_per_launch.objects.filter(item__in=items, production_operation_num=1):
            ed_izm_str = ",".join(production_order.edizm_arr) if production_order.edizm_arr is not None else ''
            value += production_order.value_sum if production_order.value_start is None else production_order.value_start

            if value > 0:
                if callbackData is not None and (
                        value == ToDecimal(callbackData.get('value')) and
                        qty == ToDecimal(callbackData.get('qty')) and
                        ed_izm_str == callbackData.get('ed_izm_str', '') and
                        production_order.item.id == callbackData.get('item_id') and
                        production_order.launch.id == callbackData.get('launch_id')):
                    return None

                if callbackData is None:
                    message_str = blinkString(
                        text=f'''{production_order.item.item_name} (ID={production_order.item.id}) присутствует в запуске {production_order.launch.code} от {DateToStr(production_order.launch.date)} на:\n{production_order.location.full_name} в количестве {DecimalToStr(value)} {ed_izm_str}, Запустить дополнительно?''',
                        blink=False,
                        color=blue, bold=True)

                    WebSocket.send_ask_message(
                        host=settings.WS_HOST,
                        port=settings.WS_PORT,
                        channel=f'common_{user.username}',
                        message=message_str,
                        callbackData=dict(
                            item_id=production_order.item.id,
                            launch_id=production_order.launch.id,
                            user_id=user.id,
                            value=value,
                            qty=qty,
                            launch__date=launch__date,
                            ed_izm=ed_izm_str
                        ),
                        logger=logger
                    )
                    return production_order
                else:
                    return None
        return None

    def make_production_order_by_hand(self, data, user):
        from django.db import transaction
        from kaf_pas.production.models.launches import Launches
        from kaf_pas.planing.models.production_order_values_ext import Production_orderWrapper

        with transaction.atomic():
            logger.debug(f'data={data}')

            callbackData = data.get('callbackData')
            item_id = data.get('item_id')
            qty = data.get('qty')
            launch__date = data.get('launch__date')

            if callbackData is not None and item_id is None:
                setAttr(data, 'item_id', callbackData.get('item_id'))

            if callbackData is not None and qty is None:
                setAttr(data, 'qty', callbackData.get('qty'))

            if callbackData is not None and launch__date is None:
                setAttr(data, 'launch__date', callbackData.get('launch__date'))

            data = Production_orderWrapper(**data)

            parentlaunch, create = Launches.objects.get_or_create(
                code='000',
                defaults=dict(
                    date=datetime.now(),
                    status=settings.PROD_OPERS_STACK.HANDMADE
                )
            )

            if self.check_exists_in_production(item=data.item, qty=data.qty, user=user, launch__date=launch__date, callbackData=callbackData) is not None:
                return

            key = f'LaunchesManager.make_production_order_by_hand{data.item_id}'
            settings.LOCKS.acquire(key)

            try:
                launches_ext = Launches_ext()
                date = StrToDate(data.launch__date)

                # Составляем производственную спецификацию
                _, launch = launches_ext.rec_launch(
                    date=date,
                    description=data.description,
                    item=data.item,
                    key=key,
                    mode='update',
                    parentlaunch=parentlaunch,
                    qty=data.qty,
                    user=user,
                )
                logger.debug(f'launch: {launch}')

                # Составляем производственную маршрутизацию
                # routing_ext = Routing_ext()
                #
                # data = dict(
                #     user=user,
                #     data=[parentlaunch.id])
                #
                # routing_ext.make_routing(data=data)

                # Составляем задания на производство

                # self.make_production_order(data=data, status_name=new_man)

                settings.LOCKS.release(key)
                # raise NotImplement()
            except Exception as ex:
                settings.LOCKS.release(key)
                raise ex
