import logging

from django.db.models import TextField

from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditManager
from kaf_pas.planing.models.operations import Operations, BaseOperationQuerySet

logger = logging.getLogger(__name__)


class Operation_noteQuerySet(BaseOperationQuerySet):
    pass


class Operation_noteManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
            'note': record.note,
        }
        return res

    def get_queryset(self):
        return Operation_noteQuerySet(self.model, using=self._db)


class Operation_note(AuditModel):
    operation = ForeignKeyCascade(Operations)
    note = TextField(db_index=True)

    objects = Operation_noteManager()

    def __str__(self):
        return f"ID:{self.id}"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица значений операции'
        unique_together = (('operation', 'note'),)
