import logging

from bitfield import BitField
from django.conf import settings
from django.db import transaction
from django.db.models import PositiveIntegerField, UniqueConstraint, Q
from django.forms import model_to_dict

from isc_common import delAttr, setAttr, Wrapper
from isc_common.fields.description_field import DescriptionField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsQuerySet, CommonManagetWithLookUpFieldsManager
from isc_common.models.base_ref import Hierarcy
from isc_common.models.standard_colors import Standard_colors
from isc_common.ws.webSocket import WebSocket
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.item import Item
from kaf_pas.production.models.operations import Operations

logger = logging.getLogger(__name__)


class Operations_itemQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def get_range_rows1(self, request, function=None, distinct_field_names=None, remove_fields=None):
        request = DSRequest(request=request)
        request.set_sort_by('num')

        self.alive_only = request.alive_only
        self.enabledAll = request.enabledAll
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

    def create(self, **kwargs):
        if kwargs.get('props') is None:
            setAttr(kwargs, 'props', Operations_item.props.created)
        return super().create(**kwargs)

    def update(self, **kwargs):
        if kwargs.get('props') is None:
            setAttr(kwargs, 'props', Operations_item.props.updated)
        return super().update(**kwargs)


class OI_Wrapper(Wrapper):
    id = None
    item_id = None
    color_id = None
    operation = None
    num = None
    dropIndex = None
    dropPosition = None


class Operations_itemManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def refreshRows(ids):
        if isinstance(ids, int):
            ids = [ids]
        records = [Operations_itemManager.getRecord(record) for record in Operations_item.objects.filter(id__in=ids)]
        WebSocket.row_refresh_grid(grid_id=settings.GRID_CONSTANTS.refresh_production_operations_grid_row, records=records)

    @staticmethod
    def fullRows(suffix=''):
        WebSocket.full_refresh_grid(grid_id=f'{settings.GRID_CONSTANTS.refresh_production_operations_grid}{suffix}')

    @staticmethod
    def props():
        return BitField(flags=(
            ('created', 'Операция добавлена'),  # 1
            ('updated', 'Операция изменена'),  # 2
        ), default=0, db_index=True)

    @staticmethod
    def refresh_num1():
        key = 'Operations_itemManager.refresh_num1'
        settings.LOCKS.acquire(key)
        cnt = 0

        with transaction.atomic():
            for operations_item in Operations_item.objects.values('item').distinct():
                num = 1
                for operations_item in Operations_item.objects.filter(item_id=operations_item.get('item')).order_by('num'):
                    if operations_item.num != num:
                        operations_item.num = num
                        operations_item.save()
                        cnt += 1
                    num += 1
        settings.LOCKS.release(key)
        return cnt

    @staticmethod
    def refresh_num(apps, schema_editor):
        Operations_itemManager.refresh_num1()

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'operation_id': record.operation.id,
            'operation__code': record.operation.code,
            'operation__name': record.operation.name,
            'operation__full_name': record.operation.full_name,
            'operation__full_name_real': record.operation.full_name,
            'operation__description': record.operation.description,
            'ed_izm_id': record.ed_izm.id if record.ed_izm else None,
            'ed_izm__code': record.ed_izm.code if record.ed_izm else None,
            'ed_izm__name': record.ed_izm.name if record.ed_izm else None,
            'ed_izm__description': record.ed_izm.description if record.ed_izm else None,
            'qty': record.qty,
            'num': record.num,
            'isDeleted': record.is_deleted,
            'description': record.description,
            'parent_id': record.parent.id if record.parent else None,
            'editing': record.editing,
            'deliting': record.deliting,

            'color__color': record.color.color if record.color else None,
            'color__name': record.color.name if record.color else None,
            'color_id': record.color.id if record.color else None,
        }
        return res

    def get_queryset(self):
        return Operations_itemQuerySet(self.model, using=self._db)

    def _rec_def_resources(self, operationitem):
        from kaf_pas.production.models.operation_def_resources import Operation_def_resources
        from kaf_pas.production.models.operation_resources import Operation_resources

        query = Operation_def_resources.objects.filter(operation=operationitem.operation)
        if query.count() > 1:
            raise Exception('К данному типу операции по-умолчанию привязано более одного ресурса или места выполнения.')

        for operation_def_resource in Operation_def_resources.objects.filter(operation=operationitem.operation):
            Operation_resources.objects.get_or_create(
                operationitem=operationitem,
                resource=operation_def_resource.resource,
                location=operation_def_resource.location,
                location_fin=operation_def_resource.location_fin,
            )

    def createFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()

        data = OI_Wrapper(**data.copy())

        delAttr(_data, 'operation__full_name')
        delAttr(_data, 'operation')

        res = []
        if isinstance(data.operation, list):
            with transaction.atomic():
                if isinstance(data.item_id, int):
                    for oparation in data.operation:
                        setAttr(_data, 'operation_id', oparation)
                        _res, created = super().get_or_create(**_data)
                        if created:
                            self._rec_def_resources(_res)
                            __res = model_to_dict(_res)
                            setAttr(__res, 'operation__full_name', _res.operation.full_name)
                            res.append(__res)
                elif isinstance(data.item_id, list):
                    delAttr(_data, 'item_id')
                    for oparation in data.operation:
                        for item in data.item_id:
                            setAttr(_data, 'operation_id', oparation)
                            setAttr(_data, 'item_id', item)
                            _res, created = super().get_or_create(**_data)
                            if created:
                                self._rec_def_resources(_res)
                                __res = model_to_dict(_res)
                                setAttr(__res, 'operation__full_name', _res.operation.full_name)
                                res.append(__res)

        Operations_itemManager.fullRows()
        return res

    @staticmethod
    def check_tansport_operations(operations_item, operation_item=None, errors_set=None):
        from kaf_pas.production.models.operation_resources import Operation_resources
        from kaf_pas.production.models.operation_def_resources import Operation_def_resources

        if not isinstance(operations_item, list):
            raise Exception('operations_item must be list')

        def check_location(operation_resources, cont):
            if operation_resources.location is None:
                if errors_set is not None:
                    operation_resources.operationitem.delete()
                    errors_set.add(f'К операции: {operation_resources.operationitem.operation.full_name} не привязано местоположение. И была удалана.')
                    return False
                else:
                    raise Exception(f'Товарная позиция: {operation_item.item.item_name}, операция: {operation_resources.operation.full_name} не привязано местоположение.')
            elif operation_resources.location.is_workshop:
                if errors_set is not None:
                    def_operation_resources = Operation_def_resources.objects.get(operation=operation_resources.operationitem.operation)
                    if def_operation_resources.location.is_workshop:
                        errors_set.add(f'Операция: {operation_resources.operationitem.operation.full_name} привязана на уровне цеха.')
                        return False
                    else:
                        operation_resources.location = def_operation_resources.location
                        operation_resources.location_fin = def_operation_resources.location_fin
                        operation_resources.save()

                else:
                    raise Exception(f'Товарная позиция: {operation_item.item.item_name}, операция: {operation_resources.operationitem.operation.full_name} привязана на уровне цеха.')

            return cont

        if operation_item.operation.props.mask == Operations.props.transportation.mask and len(operations_item) > operation_item.num:

            cont = True

            try:
                operation_resources = Operation_resources.objects.get(operationitem=operation_item)
            except Operation_resources.DoesNotExist:
                try:
                    operation_resources = Operation_def_resources.objects.get(operation=operation_item.operation)
                except Operation_def_resources.DoesNotExist:
                    errors_set.add(f'К операции: {operation_item.operation.full_name} не привязан ресурс.')
                    cont = False

            if cont == True:
                operation_before = operations_item[operation_item.num - 2]
                operation_after = operations_item[operation_item.num]

                try:
                    operation_resources_before = Operation_resources.objects.get(operationitem=operation_before)
                    cont = check_location(operation_resources=operation_resources_before, cont=cont)
                except Operation_resources.DoesNotExist:
                    try:
                        operation_resources_before = Operation_def_resources.objects.get(operation=operation_before.operation)
                        cont = check_location(operation_resources=operation_resources_before, cont=cont)

                    except Operation_def_resources.DoesNotExist:
                        if errors_set is not None:
                            operation_before.delete()
                            errors_set.add(f'К операции: {operation_before.operation.full_name} не привязано местоположение. И была удалана.')
                            cont = False
                        else:
                            raise Exception(f'Товарная позиция: {operation_item.item.item_name}, операция: {operation_before.operation.full_name} не привязано местоположение.')

                try:
                    operation_resources_after = Operation_resources.objects.get(operationitem=operation_after)
                    cont = check_location(operation_resources=operation_resources_after, cont=cont)
                except Operation_resources.DoesNotExist:
                    try:
                        operation_resources_after = Operation_def_resources.objects.get(operation=operation_after.operation)
                        cont = check_location(operation_resources=operation_resources_after, cont=cont)

                    except Operation_def_resources.DoesNotExist:
                        if errors_set is not None:
                            operation_after.delete()
                            errors_set.add(f'К операции: {operation_after.operation.full_name} не привязано местоположение. И была удалана.')
                            cont = False
                        else:
                            raise Exception(f'Товарная позиция: {operation_item.item.item_name}, операция: {operation_after.operation.full_name} не привязано местоположение.')

                if cont == True:
                    if operation_resources.location != operation_resources_before.location or \
                            operation_resources.location_fin != operation_resources_after.location:

                        using_another_place = Operations_item.objects.filter(operation=operation_item.operation).exclude(id=operation_item.id).count() > 0

                        if using_another_place:
                            try:
                                operation_def_resources = Operation_def_resources.objects.get(
                                    operation=operation_item.operation,
                                    resource=operation_resources.resource,
                                    location=operation_resources_before.location,
                                    location_fin=operation_resources_after.location,
                                )
                                operation = operation_def_resources.operation
                                logger.debug(f'exists operation: {operation}')
                            except Operation_def_resources.DoesNotExist:
                                operation, created = Operations.objects.get_or_create(
                                    code=f'{operation_resources_before.location.code}-{operation_resources_after.location.code}',
                                    defaults=dict(
                                        name='Транспортировка',
                                        props=Operations.props.transportation,
                                        parent=operation_item.operation.parent
                                    )
                                )

                                if created:
                                    logger.debug(f'created operation: {operation}')

                                    Operation_def_resources.objects.create(
                                        operation=operation,
                                        resource=operation_resources.resource,
                                        location=operation_resources_before.location,
                                        location_fin=operation_resources_after.location,
                                    )
                                else:
                                    Operation_def_resources.objects. \
                                        filter(operation=operation). \
                                        update(
                                        resource=operation_resources.resource,
                                        location=operation_resources_before.location,
                                        location_fin=operation_resources_after.location,
                                    )

                            operation_resources.location = operation_resources_before.location
                            operation_resources.location_fin = operation_resources_after.location
                            operation_resources.save()

                            logger.debug(f'operation_item.operation: {operation_item.operation}')
                            logger.debug(f'operation: {operation}')
                            if len([a for a in operations_item if a.operation == operation]) == 0:
                                operation_item.operation = operation
                                operation_item.save()
                            else:
                                operation_item.delete()
                        else:
                            operation_resources.location = operation_resources_before.location
                            operation_resources.location_fin = operation_resources_after.location
                            operation_resources.save()

                            # operation = operation_item.operation
                            # operation.code = f'{operation_resources_before.location.code}-{operation_resources_after.location.code}'
                            # operation.name = 'Транспортировка'
                            # operation.save()

                            operation_locations_def = Operation_def_resources.objects.get(operation=operation_item.operation)
                            operation_locations_def.location = operation_resources_before.location
                            operation_locations_def.location_fin = operation_resources_after.location
                            operation_locations_def.save()

    def updateFromRequest(self, request):

        request = DSRequest(request=request)
        data = request.get_data()
        old_data = request.get_oldValues()

        if data.get('record') is not None:
            data.update(data.get('record'))
            delAttr(data, 'record')

            old_data = data

        _data = data.copy()

        data = OI_Wrapper(**data)
        data_old = OI_Wrapper(**old_data)

        if data.dropIndex is not None:
            data.num = data.dropIndex + 1

        if data.num is None:
            if data.dropIndex is not None:
                data.num = data.dropIndex + 1

        key = f'OperationsManager.make_routing_{data.id}'
        settings.LOCKS.acquire(key)

        try:
            with transaction.atomic():

                # Выравниваем нумерацию ели изменен порядок следования операций
                operation_item = Operations_item.objects.get(id=data.id)
                operations_item = list(Operations_item.objects.filter(item=operation_item.item, deleted_at=None).order_by('num'))

                if data.num != data_old.num:

                    operations_item = list(Operations_item.objects.filter(item=operation_item.item, deleted_at=None).order_by('num').exclude(id=operation_item.id))

                    num = 1
                    for oi in operations_item:
                        oi.num = num
                        oi.save()
                        num += 1

                    if data.num >= len(operations_item):
                        operations_item.append(operation_item)
                    else:
                        operations_item.insert(data.num - 1, operation_item)

                    num = 1
                    for oi in operations_item:
                        oi.num = num
                        oi.save()
                        num += 1

                # Если это транспртировочная операция, то проверяем начальную и конечные точки местарасположения
                Operations_itemManager.check_tansport_operations(
                    operations_item=operations_item,
                    operation_item=operation_item
                )

                if isinstance(_data, dict):
                    for k, v in _data.items():
                        data1 = dict()
                        if isinstance(v, dict):
                            delAttr(v, 'isDeleted')
                            delAttr(v, 'dropIndex')
                            delAttr(v, 'dropPosition')
                            for k1, v1 in v.items():
                                if k1.find('_') == -1:
                                    setAttr(data1, k1, v1)
                            setAttr(data1, '_operation', 'update')
                            res = super().filter(id=v.get('id')).update(**data1)
                            break
                        else:

                            data.num = operation_item.num
                            data1 = dict()
                            for k1, v1 in data.dict.items():
                                if k1.find('__') == -1:
                                    setAttr(data1, k1, v1)

                            delAttr(data1, 'id')
                            delAttr(data1, 'isDeleted')
                            delAttr(data1, 'dropIndex')
                            delAttr(data1, 'dropPosition')

                            res = super().filter(id=data.id).update(**data1)
                            break
                else:
                    delAttr(_data, 'operation__full_name')
                    res = super().filter(id=data.id).update(**_data)

                settings.LOCKS.release(key)
                Operations_itemManager.fullRows()
                return res
        except Exception as ex:
            settings.LOCKS.release(key)
            raise ex


class Operations_item(Hierarcy):
    color = ForeignKeyProtect(Standard_colors, null=True, blank=True)
    description = DescriptionField()
    ed_izm = ForeignKeyProtect(Ed_izm, null=True, blank=True)
    item = ForeignKeyProtect(Item)
    num = PositiveIntegerField(null=True, blank=True)
    old_num = PositiveIntegerField(db_index=True, null=True, blank=True)
    operation = ForeignKeyProtect(Operations)
    props = Operations_itemManager.props()
    qty = PositiveIntegerField(null=True, blank=True)

    objects = Operations_itemManager(alive_only=True)

    def __str__(self):
        return f"ID:{self.id}, " \
               f"num: {self.num}, " \
               f"operation: [{self.operation}], " \
               f"is_deleted: {self.is_deleted}, " \
               f"item: [{self.item}], " \
               f"id_izm: [{self.ed_izm}], " \
               f"qty: {self.qty}, " \
               f"old_num: {self.old_num}"

    class Meta:
        verbose_name = 'Кросс таблица'
        constraints = [
            UniqueConstraint(fields=['item', 'operation'], condition=Q(color=None), name='Operations_item_unique_constraint_0'),
            UniqueConstraint(fields=['color', 'item', 'operation'], name='Operations_item_unique_constraint_1'),
        ]
