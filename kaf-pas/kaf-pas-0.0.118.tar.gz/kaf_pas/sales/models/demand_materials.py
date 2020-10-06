import logging

from django.db.models import DecimalField

from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsQuerySet, CommonManagetWithLookUpFieldsManager
from isc_common.models.audit import AuditModel
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.material_askon import Material_askon
from kaf_pas.ckk.models.materials import Materials
from kaf_pas.sales.models.demand import Demand

logger = logging.getLogger(__name__)


class Demand_materialsQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    pass


class Demand_materialsManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            'material_askon_id': record.material_askon.id if record.material_askon else None,
            'material_askon__field0': record.material_askon.field0 if record.material_askon else None,

            'material_id': record.material.id if record.material else None,
            'material__name': record.material.name if record.material else None,

            'complex_name': record.complex_name,
            'complex_gost': record.complex_gost,

            'edizm_id': record.edizm.id if record.edizm is not None else None,
            'edizm__code': record.edizm.code if record.edizm is not None else None,
            'edizm__name': record.edizm.name if record.edizm is not None else None,

            'qty': record.qty,

            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res

    def get_queryset(self):
        return Demand_materialsQuerySet(self.model, using=self._db)


class Demand_materials(AuditModel):
    demand = ForeignKeyCascade(Demand)
    material = ForeignKeyProtect(Materials, null=True, blank=True)
    material_askon = ForeignKeyProtect(Material_askon, null=True, blank=True)
    edizm = ForeignKeyProtect(Ed_izm)
    qty = DecimalField(decimal_places=4, max_digits=19)

    @property
    def complex_name(self):
        if self.material:
            return f'{self.material.materials_type.full_name}{self.material.full_name}'
        else:
            return None

    @property
    def complex_gost(self):
        if self.material:
            if self.material.materials_type.gost:
                return f'{self.material.materials_type.gost} / {self.material.gost}'
            else:
                return f'{self.material.gost}'
        else:
            return None

    objects = Demand_materialsManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Кросс таблица'
