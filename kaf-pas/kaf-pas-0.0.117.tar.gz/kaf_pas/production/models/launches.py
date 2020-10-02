import logging

from bitfield import BitField
from django.conf import settings
from django.db import transaction, connection
from django.db.models import DateTimeField, PositiveIntegerField, DecimalField

from isc_common import setAttr
from isc_common.bit import TurnBitOn
from isc_common.common import blinkString, red
from isc_common.common.functions import ExecuteStoredProc
from isc_common.datetime import DateToStr
from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.base_ref import BaseRefHierarcy, BaseRefManager, BaseRefQuerySet
from isc_common.number import DelProps, DecimalToStr
from isc_common.progress import managed_progress, ProgressDroped, progress_deleted
from kaf_pas.ckk.models.item import Item
from kaf_pas.production.models.launches_ext import Launches_ext
from kaf_pas.production.models.status_launch import Status_launch
from kaf_pas.sales.models.demand import Demand

logger = logging.getLogger(__name__)
logger_timing = logging.getLogger(f'{__name__}_timing')


class LaunchesQuerySet(BaseRefQuerySet):
    pass


class LaunchesManager(BaseRefManager):
    launches_ext = Launches_ext()

    @staticmethod
    def props():
        return BitField(flags=(
            ('addload', 'запуск в несколько приемов'),
        ), default=0, db_index=True)

    def getQtyChilds(self, request):

        request = DSRequest(request=request)
        data = request.get_data()
        if isinstance(data, dict):
            records = data.get('records')
            if isinstance(records, list):
                return self.launches_ext._getQtyChilds(records=records)

    def createFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        logger.debug(f'data={data}')
        setAttr(data, 'user', request.user)
        return self.launches_ext.make_launch(data)

    def updateFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        setAttr(data, 'user', request.user)
        return self.launches_ext.make_launch(data, 'update')

    def deleteFromRequest(self, request, removed=None, ):
        from kaf_pas.planing.models.operation_launches import Operation_launches
        from kaf_pas.planing.models.operations import Operations
        from kaf_pas.planing.models.operations import OperationsManager
        from kaf_pas.planing.models.production_ext import Production_ext
        from kaf_pas.production.models.launch_item_line import Launch_item_line
        from kaf_pas.production.models.launch_item_refs import Launch_item_refs
        from kaf_pas.production.models.launch_operation_material import Launch_operations_material
        from kaf_pas.production.models.launch_operation_resources import Launch_operation_resources
        from kaf_pas.production.models.launch_operations_item import Launch_operations_item
        from kaf_pas.production.models.launches_view import Launches_viewManager
        from kaf_pas.planing.models.rouning_ext import Routing_ext
        import time

        request = DSRequest(request=request)
        res = 0
        tuple_ids = request.get_tuple_ids()
        status_demand_otkr = settings.PROD_OPERS_STACK.DEMAND_OTKR

        for id, mode in tuple_ids:
            if mode == 'hide':
                super().filter(id=id).soft_delete()
            elif mode == 'visible':
                super().filter(id=id).soft_restore()
            else:
                launches = Launches.objects.filter(parent_id=id)

                if launches.count() == 0:
                    launches = Launches.objects.filter(id=id)

                for launch in launches:
                    key = f'Delete_launch_{launch.id}'
                    settings.LOCKS.acquire(key)

                    production_ext = Production_ext()
                    routing_ext = Routing_ext()

                    if launch.parent and launch.status == settings.PROD_OPERS_STACK.HANDMADE:
                        raise Exception('Удалить корневой запуск ручного формирования, невозможно.')

                    if launch.parent and launch.parent.status == settings.PROD_OPERS_STACK.HANDMADE:
                        if launch.status == settings.PROD_OPERS_STACK.IN_PRODUCTION:
                            production_ext.delete_production_order(data=dict(data=[launch.id], user=request.user))

                        if launch.status == settings.PROD_OPERS_STACK.ROUTMADE:
                            routing_ext.clean_routing(data=dict(data=[launch.id], user=request.user))

                    query = Launch_operations_item.objects.filter(launch=launch.id)

                    with managed_progress(
                            id=f'launch_{id}_{request.user_id}',
                            qty=query.count(),
                            user=request.user_id,
                            message=f'<h3>Удаление запуска: № {launch.code} от {DateToStr(launch.date)}</h3>',
                            title='Выполнено',
                            props=TurnBitOn(0, 0)
                    ) as progress:
                        with transaction.atomic():
                            def except_func():
                                settings.LOCKS.release(key)

                            progress.except_func = except_func

                            qty, _ = Launch_item_refs.objects.filter(launch_id=launch.id).delete()
                            qty1, _ = Launch_item_line.objects.filter(launch_id=launch.id).delete()
                            qty += qty1

                            for launch_operations_item in query:
                                qty1, _ = Launch_operations_material.objects.filter(launch_operationitem=launch_operations_item).delete()
                                qty += qty1
                                qty1, _ = Launch_operation_resources.objects.filter(launch_operationitem=launch_operations_item).delete()
                                qty += qty1
                                launch_operations_item.delete()
                                qty += 1

                                opers_qty = Operation_launches.objects.filter(launch_id=launch.id).count()
                                if opers_qty > 0:
                                    with managed_progress(
                                            id=f'opers_launch_{launch.id}_{request.user_id}',
                                            qty=opers_qty,
                                            user=request.user_id,
                                            message='<h3>Удаление оперций запуска</h3>',
                                            title='Выполнено',
                                            # props=TurnBitOn(0, 0)
                                    ) as progress_opers:
                                        for operation_launches in Operation_launches.objects.filter(launch_id=launch.id):
                                            try:
                                                OperationsManager.delete_recursive(operation=operation_launches.operation, user=request.user)
                                                operation_launches.operation.delete()
                                            except Operations.DoesNotExist:
                                                pass
                                            progress_opers.step()

                                if progress.step() != 0:
                                    settings.LOCKS.release(key)
                                    raise ProgressDroped(progress_deleted)

                            # qty1, _ = super().filter(id=launch.id).delete()

                            if launch.demand is not None:
                                launch.demand.status = status_demand_otkr
                                launch.demand.save()

                            if launch.demand is not None:
                                launch.demand.status = settings.PROD_OPERS_STACK.DEMAND_OTMENA
                                launch.demand.save()
                            launch.delete()

                            if Launches.objects.filter(parent_id=id).count() == 0:
                                for operation_launches in Operation_launches.objects.filter(launch_id=id, operation__opertype_id__in=[settings.OPERS_TYPES_STACK.LAUNCH_TASK.id]):
                                    ExecuteStoredProc("delete_operation", [operation_launches.operation.id])

                                Operation_launches.objects.filter(launch_id=id).delete()
                                Launches.objects.filter(id=id).delete()

                            with connection.cursor() as cursor:
                                cursor.execute('''select count(*)
                                                    from planing_operations
                                                    where id not in (select child_id from planing_operation_refs)
                                                      and id not in (select parent_id from planing_operation_refs)''')
                                count, = cursor.fetchone()
                                if count > 0:
                                    progress.setContentsLabel(blinkString(f'Удаление : {count} подвисших операций', bold=True, color=red))
                                    progress.setQty(count)

                                    cursor.execute('''select id
                                                       from planing_operations
                                                       where id not in (select child_id from planing_operation_refs)
                                                         and id not in (select parent_id from planing_operation_refs)''')
                                    rows = cursor.fetchall()
                                    for row in rows:
                                        id, = row

                                        Operations.objects.filter(id=id).delete()
                                        if progress.step() != 0:
                                            settings.LOCKS.release(key)
                                            raise ProgressDroped(progress_deleted)

                            settings.EVENT_STACK.EVENTS_PRODUCTION_DELETE_LAUNCH.send_message(f'Выполнено удаление запуска  <h3>{launch.code} от {launch.date}</h3><p/>')

                            Launches_viewManager.fullRows()
                            settings.LOCKS.release(key)
                        time.sleep(1)

                    res += qty + qty1

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            # 'date': record.date,
            'description': record.description,
            'parent_id': record.parent.id if record.parent else None,

            'demand_id': record.demand.id if record.demand else None,
            'demand__code': record.demand.code if record.demand else None,
            # 'demand__date': record.demand.date if record.demand else None,

            'status_id': record.status.id,
            'status__code': record.status.code,
            'status__name': record.status.name,

            'qty': DecimalToStr(record.qty),
            'priority': record.priority,

            'editing': record.editing,
            'deliting': record.deliting,
        }
        return DelProps(res)

    def get_queryset(self):
        return LaunchesQuerySet(self.model, using=self._db)


class Launches(BaseRefHierarcy):
    # props = LaunchesManager.props()
    code = CodeStrictField(unique=True)
    date = DateTimeField(db_index=True)
    item = ForeignKeyProtect(Item, null=True, blank=True)
    demand = ForeignKeyProtect(Demand, null=True, blank=True)
    priority = PositiveIntegerField(db_index=True, default=0)
    qty = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    status = ForeignKeyProtect(Status_launch)

    objects = LaunchesManager()

    def up_priority(self):
        Demand.objects.filter()

    @property
    def child_launches(self):
        if self.parent is None:
            return list(Launches.objects.filter(parent=self))
        else:
            return []

    def __str__(self):
        return f"ID:{self.id}, " \
               f"code: {self.code}, " \
               f"name: {self.name}, " \
               f"description: {self.description}, " \
               f"date: {self.date}, " \
               f"status: [{self.status}], " \
               f"demand: [{self.demand}], " \
               f"qty: {self.qty}"

    class Meta:
        verbose_name = 'Запуски'
