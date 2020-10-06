import logging

from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.attr_type import Attr_type
from kaf_pas.production.models.launches import Launches
from kaf_pas.production.models.operations import Operations

logger = logging.getLogger(__name__)


class Launch_operation_attrQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    pass


class Launch_operation_attrManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'launch_operationitem_id': record.launch_operationitem.id,
            "attr_type_id": record.attr_type.id,
            "attr_type__code": record.attr_type.code,
            "attr_type__name": record.attr_type.name,
            "attr_type__full_name": record.attr_type.full_name,
            "attr_type__description": record.attr_type.description,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Launch_operation_attrQuerySet(self.model, using=self._db)


class Launch_operation_attr(AuditModel):
    operation = ForeignKeyCascade(Operations)
    attr_type = ForeignKeyProtect(Attr_type)
    launch = ForeignKeyCascade(Launches)

    objects = Launch_operation_attrManager()

    def __str__(self):
        return f"{self.id}, operation: [{self.operation}], launch: [{self.launch}], attr_type: [{self.attr_type}]"

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('operation', 'attr_type', 'launch'),)
