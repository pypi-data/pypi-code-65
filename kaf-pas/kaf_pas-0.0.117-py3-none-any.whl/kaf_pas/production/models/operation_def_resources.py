import logging

from bitfield import BitField
from django.db import transaction
from django.db.models import UniqueConstraint, Q
from django.forms import model_to_dict

from isc_common import delAttr, setAttr
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from isc_common.number import DelProps
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.production.models.operation_resources import OR_Wrapper
from kaf_pas.production.models.operations import Operations
from kaf_pas.production.models.resource import Resource

logger = logging.getLogger(__name__)


class Operation_def_resourcesQuerySet(AuditQuerySet):
    def create(self, **kwargs):
        if kwargs.get('resource'):
            setAttr(kwargs, 'resource_id', kwargs.get('resource').id)
            delAttr(kwargs, 'resource')

        if kwargs.get('location'):
            setAttr(kwargs, 'location_id', kwargs.get('location').id)
            delAttr(kwargs, 'location')

        if kwargs.get('resource_fin'):
            setAttr(kwargs, 'resource_fin_id', kwargs.get('resource_fin').id)
            delAttr(kwargs, 'resource_fin')

        if kwargs.get('location'):
            setAttr(kwargs, 'location_fin_id', kwargs.get('location_fin').id)
            delAttr(kwargs, 'location_fin')

        if not kwargs.get('resource_id') and not kwargs.get('location_id'):
            raise Exception('Необходим хотябы один выбранный параметр.')

        delAttr(kwargs, 'resource__name')
        delAttr(kwargs, 'resource_fin__name')
        delAttr(kwargs, 'location__full_name')
        delAttr(kwargs, 'location_fin__full_name')
        delAttr(kwargs, 'location__code')

        resource_id = kwargs.get('resource_id')
        if resource_id:
            setAttr(kwargs, 'location_id', Resource.objects.get(id=resource_id).location.id)

        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Operation_def_resourcesManager(AuditManager):

    def allUpdateFromRequest(self, request):
        from kaf_pas.production.models.operations_item import Operations_item
        from kaf_pas.production.models.operation_resources import Operation_resources

        request = DSRequest(request=request)
        data = request.get_data()
        qty = 0

        with transaction.atomic():
            for operation_def_resource in super().filter(id__in=data.get('ids')).select_for_update():
                for operation_item in Operations_item.objects.filter(operation=operation_def_resource.operation):
                    operation_resource, created = Operation_resources.objects.update_or_create(
                        operationitem=operation_item,
                        defaults=dict(
                            resource=operation_def_resource.resource,
                            resource_fin=operation_def_resource.resource_fin,
                            location=operation_def_resource.location,
                            location_fin=operation_def_resource.location_fin,
                        )
                    )
                    if created:
                        logger.debug(f'Created: {operation_resource}')
                qty += 1

        return qty

    def updateFromRequest(self, request):

        request = DSRequest(request=request)
        data = request.get_data()

        _data = OR_Wrapper(**data)

        if _data.resource_id:
            _data.location_id = Resource.objects.get(id=_data.resource_id).location.id

        if _data.resource_fin_id:
            _data.location_fin_id = Resource.objects.get(id=_data.resource_fin_id).location.id

        if _data.location_fin_id is None and _data.location_fin__code is not None:
            _data.location_fin_id = Locations.objects.get(code=_data.location_fin__code).id

        _data = self.delete_dbl_underscore_element(_data.dict)

        with transaction.atomic():

            delAttr(_data, 'id')
            delAttr(_data, 'complex_name')
            delAttr(_data, 'rec_default')

            res, created = super().update_or_create(id=request.get_id(), defaults=_data)
            setAttr(data, 'id', res.id)
        return data

    def createFromRequest(self, request):
        from kaf_pas.production.models.operations_item import Operations_item
        from kaf_pas.production.models.operation_resources import Operation_resources

        with transaction.atomic():
            request = DSRequest(request=request)
            data = request.get_data()

            _data = OR_Wrapper(**data)

            if _data.resource_id:
                _data.location_id = Resource.objects.get(id=_data.resource_id).location.id

            if _data.resource_fin_id:
                _data.location_fin_id = Resource.objects.get(id=_data.resource_fin_id).location.id

            _data = self.delete_dbl_underscore_element(_data.dict)

            rec_default = _data.get('rec_default')
            delAttr(_data, 'rec_default')
            operation_id = _data.get('operation_id')

            res = []

            def rec_defaults(operation, operation_resource):
                if rec_default:
                    for operationitem in Operations_item.objects.filter(operation_id=operation):
                        if Operation_resources.objects.filter(operationitem=operationitem).count() == 0:
                            operation_resources, created = Operation_resources.objects.get_or_create(
                                operationitem=operationitem,
                                location=operation_resource.location,
                                location_fin=operation_resource.location_fin,
                                resource=operation_resource.resource,
                                resource_fin=operation_resource.resource_fin,
                            )
                            if created:
                                logger.debug(f'operation_resources: {operation_resources}')

            if isinstance(operation_id, list):
                delAttr(_data, 'operation_id')
                for operation in operation_id:
                    setAttr(_data, 'operation_id', operation)
                    operation_resource = super().create(**_data)
                    _res = DelProps(model_to_dict(operation_resource))
                    setAttr(_res, 'location__full_name', operation_resource.location.full_name if operation_resource.location else None)
                    setAttr(_res, 'location_fin__full_name', operation_resource.location_fin.full_name if operation_resource.location_fin else None)
                    setAttr(_res, 'resource__name', operation_resource.resource.full_name if operation_resource.resource else None)
                    setAttr(_res, 'resource_fin__name', operation_resource.resource_fin.full_name if operation_resource.resource_fin else None)
                    res.append(_res)

                    rec_defaults(operation=operation, operation_resource=operation_resource)
            else:
                operation_resource = super().create(**_data)
                _res = DelProps(model_to_dict(operation_resource))
                setAttr(_res, 'location__full_name', operation_resource.location.full_name if operation_resource.location else None)
                setAttr(_res, 'location_fin__full_name', operation_resource.location_fin.full_name if operation_resource.location_fin else None)
                setAttr(_res, 'resource_fin__name', operation_resource.resource_fin.full_name if operation_resource.resource_fin else None)
                res.append(_res)
                rec_defaults(operation=operation_id, operation_resource=operation_resource)
            return res

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'operation_id': record.operation.id,
            'resource_id': record.resource.id if record.resource else None,
            'resource__code': record.resource.code if record.resource else None,
            'resource__name': record.resource.name if record.resource else None,
            'resource_fin_id': record.resource_fin.id if record.resource_fin else None,
            'resource_fin__code': record.resource_fin.code if record.resource_fin else None,
            'resource_fin__name': record.resource_fin.name if record.resource_fin else None,
            'location_id': record.location.id if record.location else None,
            'location__code': record.location.code if record.location else None,
            'location__name': record.location.name if record.location else None,
            'location__full_name': record.location.full_name if record.location else None,
            'location_fin__code': record.location_fin.code if record.location_fin else None,
            'location_fin__name': record.location_fin.name if record.location_fin else None,
            'location_fin__full_name': record.location_fin.full_name if record.location_fin else None,
            'complex_name': record.complex_name,
            'editing': record.editing,
            'deliting': record.deliting,
            'rec_default': record.props.rec_default,
            'props': record.props,
        }
        return DelProps(res)

    @staticmethod
    def props():
        return BitField(flags=(
            ('rec_default', 'Записать ресурс по умолчанию на все операции на которых нет ресурсов'),  # 1
        ), default=0, db_index=True)

    def get_queryset(self):
        return Operation_def_resourcesQuerySet(self.model, using=self._db)


class Operation_def_resources(AuditModel):
    operation = ForeignKeyCascade(Operations)
    resource = ForeignKeyProtect(Resource, null=True, blank=True, related_name='Operation_def_resources_resource')
    resource_fin = ForeignKeyProtect(Resource, null=True, blank=True, related_name='Operation_def_resources_fin')
    location = ForeignKeyProtect(Locations, null=True, blank=True, related_name='Operation_def_resources_location')
    location_fin = ForeignKeyProtect(Locations, null=True, blank=True, related_name='Operation_def_resources_location_fin')
    props = Operation_def_resourcesManager.props()

    @property
    def complex_name(self):
        return f'{self.resource.location.full_name}{self.resource.name}' if self.resource else None

    objects = Operation_def_resourcesManager()

    def __str__(self):
        return f"{self.id}, operation: [{self.operation}], resource: [{self.resource}], location: [{self.location}], location_fin: [{self.location_fin}]"

    class Meta:
        verbose_name = 'Кросс таблица'
        constraints = [
            UniqueConstraint(fields=['operation', 'resource'], condition=Q(location=None) & Q(location_fin=None) & Q(resource_fin=None), name='Operation_def_resources_unique_constraint_1'),
            UniqueConstraint(fields=['operation', 'resource_fin'], condition=Q(location=None) & Q(location_fin=None) & Q(resource=None), name='Operation_def_resources_unique_constraint_2'),
            UniqueConstraint(fields=['operation', 'resource', 'resource_fin'], condition=Q(location=None) & Q(location_fin=None), name='Operation_def_resources_unique_constraint_3'),
            UniqueConstraint(fields=['location_fin', 'operation'], condition=Q(location=None) & Q(resource=None) & Q(resource_fin=None), name='Operation_def_resources_unique_constraint_4'),
            UniqueConstraint(fields=['location_fin', 'operation', 'resource'], condition=Q(location=None) & Q(resource_fin=None), name='Operation_def_resources_unique_constraint_5'),
            UniqueConstraint(fields=['location_fin', 'operation', 'resource_fin'], condition=Q(location=None) & Q(resource=None), name='Operation_def_resources_unique_constraint_6'),
            UniqueConstraint(fields=['location_fin', 'operation', 'resource', 'resource_fin'], condition=Q(location=None), name='Operation_def_resources_unique_constraint_7'),
            UniqueConstraint(fields=['location', 'operation'], condition=Q(location_fin=None) & Q(resource=None) & Q(resource_fin=None), name='Operation_def_resources_unique_constraint_8'),
            UniqueConstraint(fields=['location', 'operation', 'resource'], condition=Q(location_fin=None) & Q(resource_fin=None), name='Operation_def_resources_unique_constraint_9'),
            UniqueConstraint(fields=['location', 'operation', 'resource_fin'], condition=Q(location_fin=None) & Q(resource=None), name='Operation_def_resources_unique_constraint_10'),
            UniqueConstraint(fields=['location', 'operation', 'resource', 'resource_fin'], condition=Q(location_fin=None), name='Operation_def_resources_unique_constraint_11'),
            UniqueConstraint(fields=['location', 'location_fin', 'operation'], condition=Q(resource=None) & Q(resource_fin=None), name='Operation_def_resources_unique_constraint_12'),
            UniqueConstraint(fields=['location', 'location_fin', 'operation', 'resource'], condition=Q(resource_fin=None), name='Operation_def_resources_unique_constraint_13'),
            UniqueConstraint(fields=['location', 'location_fin', 'operation', 'resource_fin'], condition=Q(resource=None), name='Operation_def_resources_unique_constraint_14'),
            UniqueConstraint(fields=['location', 'location_fin', 'operation', 'resource', 'resource_fin'], name='Operation_def_resources_unique_constraint_15'),
        ]
