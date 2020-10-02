import logging

from django.db.models import UniqueConstraint, Q

from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.models.audit import AuditManager, AuditModel
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.planing.models.operations import Operations, BaseOperationQuerySet
from kaf_pas.production.models.resource import Resource

logger = logging.getLogger(__name__)


class Operation_resourcesQuerySet(BaseOperationQuerySet):
    pass


class Operation_resourcesManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Operation_resourcesQuerySet(self.model, using=self._db)


class Operation_resources(AuditModel):
    operation = ForeignKeyCascade(Operations, related_name='planing_operation_res')
    location_fin = ForeignKeyProtect(Locations, related_name='planing_location_fin_res', null=True, blank=True)
    resource = ForeignKeyProtect(Resource, related_name='planing_resource_res')
    resource_fin = ForeignKeyProtect(Resource, related_name='planing_resource_fin_res', null=True, blank=True)

    objects = Operation_resourcesManager()

    def __str__(self):
        return f"ID:{self.id}, \n" \
               f"operation: [{self.operation}], \n" \
               f"location_fin: [{self.location_fin}], \n" \
               f"resource: [{self.resource}]\n"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        constraints = [
            UniqueConstraint(fields=['operation', 'resource'], condition=Q(location_fin=None) & Q(resource_fin=None), name='Operation_resources_unique_constraint_planing_0'),
            UniqueConstraint(fields=['operation', 'resource', 'resource_fin'], condition=Q(location_fin=None), name='Operation_resources_unique_constraint_planing_1'),
            UniqueConstraint(fields=['location_fin', 'operation', 'resource'], condition=Q(resource_fin=None), name='Operation_resources_unique_constraint_planing_2'),
            UniqueConstraint(fields=['location_fin', 'operation', 'resource', 'resource_fin'], name='Operation_resources_unique_constraint_planing_3'),

        ]
