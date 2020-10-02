import logging

from django.db import transaction
from django.db.models import TextField

from isc_common import delAttr, setAttr
from isc_common.common import deleted
from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.date_time_field import DateTimeField
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.models.audit_history import AuditHistory, AuditHistoryManager, AuditHistoryQuerySet
from isc_common.number import model_2_dict
from kaf_pas.planing.models.operation_types import Operation_types
from kaf_pas.planing.models.operations import Operations
from kaf_pas.planing.models.status_operation_types import Status_operation_types, Status_operation_typesManager

logger = logging.getLogger(__name__)


class Operation_historyQuerySet(AuditHistoryQuerySet):

    def update(self, **kwargs):
        with transaction.atomic():
            operation_id = kwargs.get('id')
            creator_id = kwargs.get('creator_id')

            delAttr(kwargs, 'id')
            delAttr(kwargs, 'parent_id')
            delAttr(kwargs, 'creator_id')
            setAttr(kwargs, 'hcreator_id', creator_id)
            setAttr(kwargs, 'operation_id', operation_id)

            res = super().create(**kwargs)

            logger.debug(f'operation: {Operations.objects.get(id=operation_id)}')
            return res

    def delete(self):
        with transaction.atomic():
            for operation in self:
                kwargs = model_2_dict(operation)
                delAttr(kwargs, 'id')
                setAttr(kwargs, 'status', Status_operation_typesManager.get_status(opertype_id=kwargs.get('opertype_id'), code=deleted))
                res = super().create(**kwargs)

                logger.debug(f'operation: {operation}')
                return res


class Operation_historyManager(AuditHistoryManager):

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
        return Operation_historyQuerySet(self.model, using=self._db)


class Operation_history(AuditHistory):
    date = DateTimeField()
    description = TextField(null=True, blank=True)
    num = CodeStrictField()
    operation = ForeignKeyCascade(Operations)
    opertype = ForeignKeyProtect(Operation_types)
    status = ForeignKeyProtect(Status_operation_types)

    objects = Operation_historyManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'История операций'
