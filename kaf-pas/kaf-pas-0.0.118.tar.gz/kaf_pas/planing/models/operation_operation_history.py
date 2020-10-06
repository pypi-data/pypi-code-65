import logging

from django.db.models import PositiveIntegerField

import kaf_pas
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.models.audit_history import AuditHistory, AuditHistoryManager, AuditHistoryQuerySet
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.planing.models.operation_operation import Operation_operation, Operation_operationManager

logger = logging.getLogger(__name__)


class Operation_operation_historyQuerySet(AuditHistoryQuerySet):
    pass


class Operation_operation_historyManager(AuditHistoryManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Operation_operation_historyQuerySet(self.model, using=self._db)


class Operation_operation_history(AuditHistory):
    operation_operation = ForeignKeyCascade(Operation_operation)

    ed_izm = ForeignKeyProtect(Ed_izm, null=True, blank=True)
    num = PositiveIntegerField(db_index=True)
    operation = ForeignKeyCascade(kaf_pas.planing.models.operations.Operations)
    production_operation = ForeignKeyCascade(kaf_pas.production.models.operations.Operations)
    qty = PositiveIntegerField(null=True, blank=True, db_index=True)
    # version = PositiveIntegerField(null=True, blank=True, db_index=True)
    creator = ForeignKeyProtect(User, related_name='Operation_operation_history_creator')
    props = Operation_operationManager.props()

    objects = Operation_operation_historyManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'История операций'
