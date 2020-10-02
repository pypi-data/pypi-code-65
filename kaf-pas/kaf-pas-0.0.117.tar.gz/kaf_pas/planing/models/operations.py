import logging

from django.conf import settings
from django.db import transaction
from django.db.models import TextField, DateTimeField
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.forms import model_to_dict

from isc_common import delAttr, setAttr
from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditQuerySet
from isc_common.models.base_ref import Hierarcy, BaseRefQuerySet
from isc_common.number import DelProps, model_2_dict, flen
from isc_common.progress import managed_progress, ProgressDroped, progress_deleted
from kaf_pas.planing.models.operation_types import Operation_types
from kaf_pas.planing.models.status_operation_types import Status_operation_types

logger = logging.getLogger(__name__)


class BaseOperationQuerySet(AuditQuerySet):
    def delete(self):
        from kaf_pas.planing.models.production_order import Production_orderManager

        for this in self:
            if isinstance(this, Operations):
                if this.opertype == settings.OPERS_TYPES_STACK.PRODUCTION_TASK:
                    Production_orderManager.delete_redundant_planing_production_order_table(this)
        return super().delete()


class OperationsQuerySet(BaseRefQuerySet, CommonManagetWithLookUpFieldsQuerySet, BaseOperationQuerySet):

    def create(self, **kwargs):
        from isc_common.seq import get_deq_next_value

        if kwargs.get('num') is None:
            setAttr(kwargs, 'num', str(get_deq_next_value('production_order_num')))

        with transaction.atomic():
            res = super().create(**kwargs)
            delAttr(kwargs, 'creator')
            delAttr(kwargs, 'parent')
            setAttr(kwargs, 'operation', res)
            setAttr(kwargs, 'operation', res)
            setAttr(kwargs, 'hcreator', res.creator)
            return res

    def update(self, **kwargs):

        with transaction.atomic():
            res = super().update(**kwargs)

            for operation in self:
                operation = model_2_dict(operation)
                setAttr(operation, 'operation_id', operation.get('id'))
                setAttr(operation, 'hcreator_id', operation.get('creator_id'))
                delAttr(operation, 'id')
                delAttr(operation, 'parent_id')
                delAttr(operation, 'creator_id')
            return res


class OperationsManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def check_refs_free(operation_id):
        from kaf_pas.planing.models.operation_refs import Operation_refs
        return Operation_refs.objects.filter(child_id=operation_id).count() == 0 and Operation_refs.objects.filter(parent_id=operation_id).count() == 0

    @staticmethod
    def delete_recursive(operation, user, soft_delete=False, opertypes=None, pre_delete_function=None, lock=True):
        from kaf_pas.planing.models.operation_refs import Operation_refs
        key = f'OperationsManager.delete_recursive_{operation.id}'
        if lock:
            settings.LOCKS.acquire(key)

        sql_text = f'''WITH RECURSIVE r AS (
                                                    SELECT cir.*, cich.opertype_id, 1 AS level
                                                    FROM planing_operation_refs cir
                                                             join planing_operations cich on cich.id = cir.child_id
                                                    WHERE cir.child_id IN ({operation.id})

                                                    union all

                                                    SELECT cir.* , cich.opertype_id , r.level + 1 AS level
                                                    FROM planing_operation_refs cir
                                                             join planing_operations cich on cich.id = cir.child_id
                                                             JOIN r ON cir.parent_id = r.child_id
                                                )

                                                    select *  from r
                                                      where opertype_id in  ({opertypes})
                                                     order by level desc'''

        count = Operation_refs.objects.get_descendants_count(id=operation.id, sql_text=sql_text if opertypes is not None else None)
        operations = set()

        if count > 0:
            with managed_progress(
                    id=operation.id,
                    qty=count,
                    user=user,
                    message='Удаление связанных операций операций',
                    title='Выполнено',
                    # props=TurnBitOn(0, 0)
            ) as progress:
                # with transaction.atomic():
                for operation_refs in Operation_refs.objects.get_descendants(
                        id=operation.id,
                        sql_text=sql_text if opertypes is not None else None):
                    if not soft_delete:
                        Operation_refs.objects.filter(id=operation_refs.id).delete()
                        operations.add(operation_refs.child.id)
                    else:
                        Operation_refs.objects.filter(id=operation_refs.id).soft_delete()

                    if progress.step() != 0:
                        if lock:
                            settings.LOCKS.release(key)
                        raise ProgressDroped(progress_deleted)

                if not soft_delete:
                    for operation_id in list(operations):
                        # if OperationsManager.check_refs_free(operation_id=operation_id) == True:
                        OperationsManager.delete_recursive(operation=Operations.objects.get(id=operation_id), user=user, lock=False)
                        for op in Operations.objects.filter(id=operation_id):
                            if callable(pre_delete_function):
                                pre_delete_function(operation)

                            # ExecuteStoredProc("delete_operation", [op.id])
                            for operation_refs in Operation_refs.objects.filter(parent=op):
                                try:
                                    OperationsManager.delete_recursive(operation=operation_refs.child, user=user, lock=False)
                                except Operations.DoesNotExist:
                                    pass
                            Operations.objects.filter(id=op.id).delete()

        if lock:
            settings.LOCKS.release(key)

    @staticmethod
    def set_location(location_id, operation_id, resource_id=None):
        from kaf_pas.production.models.resource import Resource
        from kaf_pas.planing.models.operation_resources import Operation_resources
        from clndr.models.calendars import CalendarsManager

        if location_id:
            resource = None
            if resource_id is None:
                try:
                    resource = Resource.objects.get(code='none', location_id=location_id)
                except Resource.DoesNotExist:
                    resource = Resource.objects.create(code='node', name='Не определен', location_id=location_id, calendar=CalendarsManager.get_default())

            if resource is None:
                resource = Resource.objects.get(id=resource_id)
                if resource.location_id != location_id:
                    resource = Resource.objects.create(location_id=location_id, calendar=resource.calendar)

            Operation_resources.objects.update_or_create(operation_id=operation_id, resource=resource)

    @staticmethod
    def set_anothers(operation_id, item_id=None, edizm_id=None, value=None, color_id=None, old_data=dict()):
        from kaf_pas.planing.models.operation_item import Operation_item
        from kaf_pas.planing.models.operation_value import Operation_value
        from kaf_pas.planing.models.operation_color import Operation_color

        if item_id:
            operation_item, created = Operation_item.objects.update_or_create(
                operation_id=operation_id,
                defaults=dict(
                    item_id=item_id,
                ))
        else:
            deleted, _ = Operation_item.objects.filter(
                operation_id=operation_id,
                item_id=old_data.get(item_id),
            ).delete()

        if edizm_id and value:
            operation_value, created = Operation_value.objects.update_or_create(
                operation_id=operation_id,
                value=old_data.get('value'),
                defaults=dict(edizm_id=edizm_id, value=value))
        else:
            deleted, _ = Operation_value.objects.filter(
                operation_id=operation_id,
                edizm_id=old_data.get('edizm_id'),
                value=old_data.get('value'),
            ).delete()

        if color_id:
            operation_color, created = Operation_color.objects.update_or_create(
                operation_id=operation_id,
                defaults=dict(color_id=color_id))
        else:
            deleted, _ = Operation_color.objects.filter(
                operation_id=operation_id,
                color_id=old_data.get('color_id'),
            ).delete()

    def createFromRequest(self, request, removed=None):
        from kaf_pas.planing.models.operation_refs import Operation_refs

        request = DSRequest(request=request)
        data = request.get_data()
        old_data = request.get_oldValues()
        _data = data.copy()
        self._remove_prop(_data, removed)

        with transaction.atomic():
            parent_id = _data.get('parent_id')
            item_id = _data.get('item_id')
            edizm_id = _data.get('edizm_id')
            value = _data.get('value')
            color_id = _data.get('color_id')
            location_id = _data.get('location_id')

            delAttr(_data, 'parent_id')
            delAttr(_data, 'item_id')
            delAttr(_data, 'edizm_id')
            delAttr(_data, 'value')
            delAttr(_data, 'color_id')
            delAttr(_data, 'location_id')

            res = super().create(**_data)

            operation_id = res.id
            Operation_refs.objects.create(parent_id=parent_id, child_id=operation_id)

            OperationsManager.set_anothers(operation_id=operation_id, item_id=item_id, edizm_id=edizm_id, color_id=color_id, value=value, old_data=old_data)
            OperationsManager.set_location(location_id=location_id, operation_id=operation_id)

            res = model_to_dict(res)
            data.update(DelProps(res))
        return data

    def updateFromRequest(self, request, removed=None, function=None):

        if not isinstance(request, DSRequest):
            request = DSRequest(request=request)
        data = request.get_data()
        old_data = request.get_oldValues()

        _data = data.copy()
        delAttr(_data, 'creator_id')
        _data.setdefault('creator_id', request.user_id)

        item_id = _data.get('item_id')
        edizm_id = _data.get('edizm_id')
        value = _data.get('value')
        color_id = _data.get('color_id')
        location_id = _data.get('location_id')
        resource_id = _data.get('resource_id')
        operation_id = _data.get('id')
        # description = _data.get('description')

        delAttr(_data, 'id')
        delAttr(_data, 'creator__short_name')

        delAttr(_data, 'opertype__full_name')
        delAttr(_data, 'isFolder')

        delAttr(_data, 'status__code')
        delAttr(_data, 'status__name')

        delAttr(_data, 'color__name')
        delAttr(_data, 'color__color')

        delAttr(_data, 'location__code')
        delAttr(_data, 'location__name')
        delAttr(_data, 'location__full_name')

        delAttr(_data, 'item__STMP_1_id')
        delAttr(_data, 'item__STMP_1__value_str')

        delAttr(_data, 'item__STMP_2_id')
        delAttr(_data, 'item__STMP_2__value_str')

        delAttr(_data, 'edizm__code')
        delAttr(_data, 'edizm__name')

        with transaction.atomic():
            OperationsManager.set_anothers(operation_id=operation_id, item_id=item_id, edizm_id=edizm_id, color_id=color_id, value=value, old_data=old_data)
            OperationsManager.set_location(location_id=location_id, resource_id=resource_id, operation_id=operation_id)

            delAttr(_data, 'item_full_name')
            delAttr(_data, 'item_full_name_obj')
            delAttr(_data, 'item_item_name')
            delAttr(_data, 'value')
            delAttr(_data, 'value_start')
            delAttr(_data, 'value_made')
            delAttr(_data, 'executors')
            delAttr(_data, 'launch__date')
            delAttr(_data, 'launch__code')
            delAttr(_data, 'launch__name')
            delAttr(_data, 'color__name')
            delAttr(_data, 'color__color')
            delAttr(_data, 'edizm_id')
            delAttr(_data, 'operation_id')

            super().filter(id=operation_id).update(**_data)
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
                    for operation in super().filter(id=id):
                        OperationsManager.delete_recursive(operation=operation, user=request.user)
                        res += 1
        return res

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'num': record.num,
            'date': record.date,
            'opertype_id': record.opertype.id,
            'opertype__full_name': record.opertype.full_name,
            'creator__short_name': record.creator.get_short_name,
            'status_id': record.status.id if record.status else None,
            'status__code': record.status.code if record.status else None,
            'status__name': record.status.name if record.status else None,
            'description': record.description,
            'isFolder': False,
        }
        return res

    def get_queryset(self):
        return OperationsQuerySet(self.model, using=self._db)


class Operations(Hierarcy):
    num = CodeStrictField()
    date = DateTimeField()
    creator = ForeignKeyProtect(User)
    opertype = ForeignKeyProtect(Operation_types)
    status = ForeignKeyProtect(Status_operation_types, related_name='planing_Operations_status')
    description = TextField(null=True, blank=True)

    objects = OperationsManager()

    # @property
    # def minus_values(self):
    #     from kaf_pas.planing.models.operation_refs import Operation_refs
    #     from kaf_pas.planing.operation_typesStack import MADE_OPRS_MNS_TSK
    #
    #     res = map(lambda x: x.child, Operation_refs.objects.filter(parent__in=map(lambda x: x.id, self.plus_values), child__opertype__code=MADE_OPRS_MNS_TSK))
    #     return res

    # @property
    # def plus_values(self):
    #     from kaf_pas.planing.models.operation_refs import Operation_refs
    #     from kaf_pas.planing.operation_typesStack import MADE_OPRS_PLS_TSK
    #
    #     return map(lambda x: x.child, Operation_refs.objects.filter(parent=self, child__opertype__code=MADE_OPRS_PLS_TSK))

    def __str__(self):
        return f"ID:{self.id}, " \
               f"date: {self.date}, " \
               f"deleted_at: {self.deleted_at}, " \
               f"description: {self.description},  " \
               f"creator: [{self.creator}], " \
               f"opertype: [{self.opertype}], " \
               f"status: [{self.status}]"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Опреации системные'


@receiver(pre_delete, sender=Operations)
def pre_delete(sender, **kwargs):
    from kaf_pas.planing.models.production_order import Production_orderManager

    instance = kwargs.get('instance')
    if instance.opertype == settings.OPERS_TYPES_STACK.PRODUCTION_TASK:
        # if flen(instance.minus_values) > 0:
        #     raise Exception(f'Удаление невозможно, есть связанные выпуски.')

        Production_orderManager.delete_redundant_planing_production_order_table(instance)
        Production_orderManager.refresh_all(
            buffer_refresh=True,
            ids=instance,
            item_operations_refresh=True,
            production_order_values_refresh=True,
            production_order_opers_refresh=True,
        )
