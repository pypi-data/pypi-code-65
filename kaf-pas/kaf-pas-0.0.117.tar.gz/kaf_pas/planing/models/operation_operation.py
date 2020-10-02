import logging

from bitfield import BitField
from django.db.models import PositiveIntegerField, UniqueConstraint, Q

import kaf_pas
from isc_common import delAttr1, setAttr, delAttr
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade, ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditModel
from isc_common.models.standard_colors import Standard_colors
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.planing.models.operations import BaseOperationQuerySet
from kaf_pas.production.models.operations import Operations

logger = logging.getLogger(__name__)


class Operation_operationQuerySet(BaseOperationQuerySet):
    def create(self, **kwargs):
        from kaf_pas.planing.models.operation_operation_history import Operation_operation_history

        self._check_ed_izm_qty(**kwargs)

        res = super().create(**kwargs)
        operation_operation_history = delAttr1(kwargs, 'id')
        delAttr(operation_operation_history, 'color')
        setAttr(operation_operation_history, 'operation_operation', res)
        setAttr(operation_operation_history, 'hcreator', res.creator)
        Operation_operation_history.objects.create(**operation_operation_history)
        return res

    def update(self, **kwargs):
        from kaf_pas.planing.models.operation_operation_history import Operation_operation_history

        self._check_ed_izm_qty(**kwargs)

        res = super().update(**kwargs)

        operation_operation_history = delAttr1(kwargs, 'id')
        delAttr(operation_operation_history, 'color')
        setAttr(operation_operation_history, 'operation_operation', res)
        setAttr(operation_operation_history, 'hcreator', res.creator)
        Operation_operation_history.objects.create(**operation_operation_history)
        return res


class Operation_operationManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    @staticmethod
    def props():
        return BitField(flags=(
            ('direct_created', 'Созданный после включения в производственную спецификацию'),  # 0-1
            ('updated', 'Обновленный'),  # 0-1
        ), default=0, db_index=True)

    def get_queryset(self):
        return Operation_operationQuerySet(self.model, using=self._db)


class Operation_operation(AuditModel):
    creator = ForeignKeyProtect(User)
    ed_izm = ForeignKeyProtect(Ed_izm, null=True, blank=True)
    num = PositiveIntegerField(db_index=True)
    operation = ForeignKeyCascade(kaf_pas.planing.models.operations.Operations, related_name='planing_operation_2')
    production_operation = ForeignKeyCascade(Operations, related_name='production_operation_2')
    props = Operation_operationManager.props()
    qty = PositiveIntegerField(null=True, blank=True, db_index=True)
    color = ForeignKeyProtect(Standard_colors, null=True, blank=True)
    # version = PositiveIntegerField(null=True, blank=True, db_index=True)

    objects = Operation_operationManager()

    def __str__(self):
        return f'ID:{self.id}, num: {self.num}, production_operation: [{self.production_operation}], operation: [{self.operation}]'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс-таблица'
        constraints = [
            UniqueConstraint(fields=['operation', 'production_operation'], condition=Q(color=None), name='Operation_operation_unique_constraint_0'),
            UniqueConstraint(fields=['color', 'operation', 'production_operation'], name='Operation_operation_unique_constraint_1'),
        ]
