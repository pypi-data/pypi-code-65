import logging

from django.db.models import BigIntegerField

from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.planing.models.levels import Levels
from kaf_pas.planing.models.operations import Operations
from kaf_pas.production.models.launches import Launches

logger = logging.getLogger(__name__)


class Operation_locationQuerySet(AuditQuerySet):
    pass


class Operation_location_viewManager(AuditManager):

    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Operation_locationQuerySet(self.model, using=self._db)


class Operation_location_view(AuditModel):
    operation = ForeignKeyCascade(Operations, related_name='Operation_location_view_operation')
    location = ForeignKeyCascade(Locations, related_name='Operation_location_view_level')
    launch = ForeignKeyCascade(Launches, related_name='Operation_location_view_launches')
    level = ForeignKeyCascade(Levels, related_name='Operation_location_view_level')
    opers_refs_props = BigIntegerField()

    objects = Operation_location_viewManager()

    def __str__(self):
        return f"ID:{self.id}, level: [{self.location}] , operation: [{self.operation}]"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс-таблица'
        managed = False
        db_table = 'planing_operation_location_view'
