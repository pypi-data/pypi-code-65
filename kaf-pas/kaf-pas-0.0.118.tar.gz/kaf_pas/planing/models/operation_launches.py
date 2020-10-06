import logging

from bitfield import BitField

from isc_common.fields.related import ForeignKeyCascade, ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager
from kaf_pas.planing.models.operations import Operations, BaseOperationQuerySet
from kaf_pas.production.models.launches import Launches

logger = logging.getLogger(__name__)


class Operation_launchesQuerySet(BaseOperationQuerySet):
    pass

class Operation_launchesManager(AuditManager):

    @staticmethod
    def props():
        return BitField(flags=(
            ('auxiliary', 'Прикрипленный запуск'),  # 0-1
        ), default=0, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Operation_launchesQuerySet(self.model, using=self._db)


class Operation_launches(AuditModel):
    operation = ForeignKeyCascade(Operations, related_name='planing_operation_launch')
    launch = ForeignKeyProtect(Launches, related_name='planing_resource_launch')
    props = Operation_launchesManager.props()

    objects = Operation_launchesManager()

    def __str__(self):
        return f"ID:{self.id}, operation: [{self.operation}], launch: [{self.launch}]"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('operation', 'launch'),)
