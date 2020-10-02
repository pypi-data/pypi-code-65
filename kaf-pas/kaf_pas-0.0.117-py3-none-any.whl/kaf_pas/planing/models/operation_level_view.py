import logging

from django.db.models import BigIntegerField

from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditManager
from kaf_pas.planing.models.levels import Levels
from kaf_pas.planing.models.operation_level import Operation_levelManager
from kaf_pas.planing.models.operations import Operations, BaseOperationQuerySet
from kaf_pas.production.models.launches import Launches

logger = logging.getLogger(__name__)


class Operation_levelQuerySet(BaseOperationQuerySet):
    pass


class Operation_level_viewManager(AuditManager):

    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Operation_levelQuerySet(self.model, using=self._db)


class Operation_level_view(AuditModel):
    operation = ForeignKeyCascade(Operations, related_name='Operation_level_view_operation')
    level = ForeignKeyCascade(Levels, related_name='Operation_level_view_level')
    launch = ForeignKeyCascade(Launches, related_name='Operation_level_view_launches')
    opers_refs_props = BigIntegerField()

    props = Operation_levelManager.props()

    objects = Operation_level_viewManager()

    def __str__(self):
        return f"ID:{self.id}, level: [{self.level}] , operation: [{self.operation}]"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс-таблица'
        managed = False
        db_table = 'planing_operation_level_view'
