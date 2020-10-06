import logging

from bitfield import BitField

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade, ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager
from kaf_pas.planing.models.operations import Operations, BaseOperationQuerySet

logger = logging.getLogger(__name__)


class Operation_executorQuerySet(BaseOperationQuerySet):
    pass


class Operation_executorManager(AuditManager):

    @staticmethod
    def props():
        return BitField(flags=(
            ('relevant', 'Актуальность'),  # 1
            ('rearrange', 'Переадресованный'),  # 1
        ), default=1, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
            'executor_id': record.executor.id,
        }
        return res

    def get_queryset(self):
        return Operation_executorQuerySet(self.model, using=self._db)


class Operation_executor(AuditModel):
    operation = ForeignKeyCascade(Operations)
    executor = ForeignKeyProtect(User)
    props = Operation_executorManager.props()

    objects = Operation_executorManager()

    def __str__(self):
        return f"ID:{self.id}, operation: [{self.operation}], executor: [{self.executor}]"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица ответственных исполнителей'
        unique_together = (('operation', 'executor'),)
