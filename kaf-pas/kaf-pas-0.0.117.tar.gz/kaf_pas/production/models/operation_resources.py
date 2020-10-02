import logging

from django.conf import settings
from django.db import transaction, connection
from django.db.models import PositiveIntegerField, OneToOneField, CASCADE, UniqueConstraint, Q
from django.forms import model_to_dict

from isc_common import delAttr, setAttr, Wrapper
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.production.models.operations_item import Operations_item
from kaf_pas.production.models.resource import Resource

logger = logging.getLogger(__name__)


class Operation_resourcesQuerySet(CommonManagetWithLookUpFieldsQuerySet):
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

        if kwargs.get('location_fin'):
            setAttr(kwargs, 'location_fin_id', kwargs.get('location_fin').id)
            delAttr(kwargs, 'location_fin')

        if not kwargs.get('resource_id') and not kwargs.get('location_id'):
            raise Exception('Не выбран ресурс или место выполнения операции.')

        delAttr(kwargs, 'resource__name')
        delAttr(kwargs, 'location__full_name')

        resource_id = kwargs.get('resource_id')
        if resource_id is not None:
            setAttr(kwargs, 'location_id', Resource.objects.get(id=resource_id).location.id)

        setAttr(kwargs, '_operation', 'create')
        return super().create(**kwargs)


class OR_Wrapper(Wrapper):
    resource_id = None
    resource_fin_id = None

    location_id = None
    location_fin_id = None
    location_fin__code = None


class Operation_resourcesManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def refresh_resource(apps=None, schema_editor=None):
        key = 'Operation_resourcesManager.refresh_resource'
        settings.LOCKS.acquire(key)
        sql_text = '''select  operationitem_id, count(*)
                    from production_operation_resources
                    group by operationitem_id
                    having count(*) > 1'''

        sql_items = '''select id
            from production_operation_resources
            where operationitem_id = %s'''

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(sql_text)
                rows = cursor.fetchall()
                for row in rows:
                    operationitem_id, count = row
                    # print(f'launch_operationitem_id: {launch_operationitem_id}')
                    cursor.execute(sql_items, [operationitem_id])
                    rows_item = cursor.fetchall()

                    first_step = True
                    for item in rows_item:
                        id, = item
                        if not first_step:
                            # print(f'id: {id}')
                            Operation_resources.objects.filter(id=id).delete()
                            # print(res)
                        else:
                            first_step = False
        settings.LOCKS.release(key)

    def createFromRequest(self, request):
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

        operationitem_id = _data.get('operationitem_id')

        res = []
        if isinstance(operationitem_id, list):
            delAttr(_data, 'operationitem_id')
            with transaction.atomic():
                for operationitem in operationitem_id:
                    setAttr(_data, 'operationitem_id', operationitem)
                    operation_resource, created = super().get_or_create(**_data)
                    if created:
                        _res = model_to_dict(operation_resource)
                        setAttr(_res, 'location__full_name', operation_resource.location.full_name if operation_resource.location else None)
                        setAttr(_res, 'location_fin__full_name', operation_resource.location_fin.full_name if operation_resource.location_fin else None)
                        setAttr(_res, 'resource__name', operation_resource.resource.name if operation_resource.resource else None)
                        setAttr(_res, 'resource_fin__name', operation_resource.resource_fin.name if operation_resource.resource_fin else None)
                        res.append(_res)
        else:
            operation_resource, created = super().get_or_create(**_data)
            if created:
                _res = model_to_dict(operation_resource)

                setAttr(_res, 'location__full_name', operation_resource.location.full_name if operation_resource.location else None)
                setAttr(_res, 'location_fin__full_name', operation_resource.location_fin.full_name if operation_resource.location_fin else None)
                setAttr(_res, 'resource__name', operation_resource.resource.full_name if operation_resource.resource else None)
                setAttr(_res, 'resource_fin__name', operation_resource.resource_fin.full_name if operation_resource.resource_fin else None)
                res.append(_res)
        return res

    def updateFromRequest(self, request, removed=None, function=None):
        if not isinstance(request, DSRequest):
            request = DSRequest(request=request)
        data = request.get_data()

        if data is None:
            data = dict()

        self._remove_prop(data, removed)
        _data = OR_Wrapper(**data)

        if _data.resource_id:
            _data.location_id = Resource.objects.get(id=_data.resource_id).location.id

        if _data.resource_fin_id:
            _data.location_fin_id = Resource.objects.get(id=_data.resource_fin_id).location.id

        if _data.location_fin_id is None and _data.location_fin__code is not None:
            _data.location_fin_id = Locations.objects.get(code=_data.location_fin__code).id

        _data = self.delete_dbl_underscore_element(_data.dict)

        delAttr(_data, 'id')
        delAttr(_data, 'complex_name')
        res = super().filter(id=data.get('id')).update(**_data)
        return res

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'operationitem_id': record.operationitem.id if record.operationitem else None,
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
            'location_fin_id': record.location_fin.id if record.location_fin else None,
            'location_fin__code': record.location_fin.code if record.location_fin else None,
            'location_fin__name': record.location_fin.name if record.location_fin else None,
            'location_fin__full_name': record.location_fin.full_name if record.location_fin else None,
            'complex_name': record.complex_name,
            'batch_size': record.batch_size,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Operation_resourcesQuerySet(self.model, using=self._db)


class Operation_resources(AuditModel):
    operationitem = OneToOneField(Operations_item, on_delete=CASCADE)
    resource = ForeignKeyProtect(Resource, null=True, blank=True, related_name='Operation_resources_resource')
    resource_fin = ForeignKeyProtect(Resource, null=True, blank=True, related_name='Operation_resources_resource_fin')
    location = ForeignKeyProtect(Locations, null=True, blank=True, related_name='Operation_resources_location')
    location_fin = ForeignKeyProtect(Locations, null=True, blank=True, related_name='Operation_resources_location_fin')
    batch_size = PositiveIntegerField(default=1)

    @property
    def complex_name(self):
        return f'{self.resource.location.full_name}{self.resource.name}' if self.resource else None

    objects = Operation_resourcesManager()

    def __str__(self):
        return f"{self.id}, operationitem: [{self.operationitem}], resource: [{self.resource}], location: [{self.location}], location_fin: [{self.location_fin}]"

    def __repr__(self):
        return str(self.resource) if self.resource else str(self.location)

    class Meta:
        verbose_name = 'Кросс таблица'
        constraints = [
            UniqueConstraint(fields=['operationitem'], condition=Q(location=None) & Q(location_fin=None) & Q(resource=None) & Q(resource_fin=None), name='Operation_resources_unique_constraint_0'),
            UniqueConstraint(fields=['operationitem', 'resource'], condition=Q(location=None) & Q(location_fin=None) & Q(resource_fin=None), name='Operation_resources_unique_constraint_1'),
            UniqueConstraint(fields=['operationitem', 'resource_fin'], condition=Q(location=None) & Q(location_fin=None) & Q(resource=None), name='Operation_resources_unique_constraint_2'),
            UniqueConstraint(fields=['operationitem', 'resource', 'resource_fin'], condition=Q(location=None) & Q(location_fin=None), name='Operation_resources_unique_constraint_3'),
            UniqueConstraint(fields=['location', 'operationitem'], condition=Q(location_fin=None) & Q(resource=None) & Q(resource_fin=None), name='Operation_resources_unique_constraint_4'),
            UniqueConstraint(fields=['location', 'operationitem', 'resource'], condition=Q(location_fin=None) & Q(resource_fin=None), name='Operation_resources_unique_constraint_5'),
            UniqueConstraint(fields=['location', 'operationitem', 'resource_fin'], condition=Q(location_fin=None) & Q(resource=None), name='Operation_resources_unique_constraint_6'),
            UniqueConstraint(fields=['location', 'operationitem', 'resource', 'resource_fin'], condition=Q(location_fin=None), name='Operation_resources_unique_constraint_7'),
            UniqueConstraint(fields=['location_fin', 'operationitem'], condition=Q(location=None) & Q(resource=None) & Q(resource_fin=None), name='Operation_resources_unique_constraint_8'),
            UniqueConstraint(fields=['location_fin', 'operationitem', 'resource'], condition=Q(location=None) & Q(resource_fin=None), name='Operation_resources_unique_constraint_9'),
            UniqueConstraint(fields=['location_fin', 'operationitem', 'resource_fin'], condition=Q(location=None) & Q(resource=None), name='Operation_resources_unique_constraint_10'),
            UniqueConstraint(fields=['location_fin', 'operationitem', 'resource', 'resource_fin'], condition=Q(location=None), name='Operation_resources_unique_constraint_111'),
            UniqueConstraint(fields=['location', 'location_fin', 'operationitem'], condition=Q(resource=None) & Q(resource_fin=None), name='Operation_resources_unique_constraint_12'),
            UniqueConstraint(fields=['location', 'location_fin', 'operationitem', 'resource'], condition=Q(resource_fin=None), name='Operation_resources_unique_constraint_13'),
            UniqueConstraint(fields=['location', 'location_fin', 'operationitem', 'resource_fin'], condition=Q(resource=None), name='Operation_resources_unique_constraint_14'),
            UniqueConstraint(fields=['location', 'location_fin', 'operationitem', 'resource', 'resource_fin'], name='Operation_resources_unique_constraint_15'),
        ]
