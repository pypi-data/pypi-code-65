import logging

from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditManager
from kaf_pas.planing.models.operations import Operations, BaseOperationQuerySet
from kaf_pas.production.models.launch_operations_item import Launch_operations_item

logger = logging.getLogger(__name__)


class Operation_launch_itemQuerySet(BaseOperationQuerySet):
    pass


class Operation_launch_itemManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Operation_launch_itemQuerySet(self.model, using=self._db)


class Operation_launch_item(AuditModel):
    operation = ForeignKeyCascade(Operations)
    launch_item = ForeignKeyCascade(Launch_operations_item)
    # operation_refs = ForeignKeyCascade(Operation_refs)

    objects = Operation_launch_itemManager()

    def __str__(self):
        return f"ID:{self.id}, \n" \
               f"operation: [{self.operation}], \n" \
               f"launch_item: [{self.launch_item}]"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('operation', 'launch_item'),)
