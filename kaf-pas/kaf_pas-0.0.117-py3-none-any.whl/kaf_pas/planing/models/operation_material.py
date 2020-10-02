import logging

from django.db.models import DecimalField, UniqueConstraint, Q

from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditManager
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.material_askon import Material_askon
from kaf_pas.ckk.models.materials import Materials
from kaf_pas.planing.models.operations import Operations, BaseOperationQuerySet

logger = logging.getLogger(__name__)


class Operation_materialQuerySet(BaseOperationQuerySet):
    pass


class Operation_materialManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Operation_materialQuerySet(self.model, using=self._db)


class Operation_material(AuditModel):
    operation = ForeignKeyCascade(Operations, related_name='planing_operation')
    edizm = ForeignKeyProtect(Ed_izm, related_name='Operation_material_edizm')
    material = ForeignKeyProtect(Materials, null=True, blank=True, related_name='Operation_material_material')
    material_askon = ForeignKeyProtect(Material_askon, null=True, blank=True, related_name='Operation_material_material_askon')
    qty = DecimalField(max_digits=10, decimal_places=4, default=0.0)

    objects = Operation_materialManager()

    def __str__(self):
        return f"ID:{self.id}, \n" \
               f"operation: [{self.operation}], \n" \
               f"material: [{self.material}], \n" \
               f"material_askon: [{self.material_askon}], \n" \
               f"edizm: [{self.edizm}], \n" \
               f"qty: {self.qty} \n"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        constraints = [
            UniqueConstraint(fields=['operation'], condition=Q(material=None) & Q(material_askon=None), name='Operation_material_unique_constraint_10'),
            UniqueConstraint(fields=['material', 'operation'], condition=Q(material_askon=None), name='Operation_material_unique_constraint_11'),
            UniqueConstraint(fields=['material_askon', 'operation'], condition=Q(material=None), name='Operation_material_unique_constraint_21'),
            UniqueConstraint(fields=['material', 'material_askon', 'operation'], name='Operation_material_unique_constraint_31'),
        ]
