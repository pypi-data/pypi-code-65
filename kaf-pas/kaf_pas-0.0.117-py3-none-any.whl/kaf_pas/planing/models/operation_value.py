import logging

from bitfield import BitField
from django.db.models import DecimalField

from isc_common.fields.related import ForeignKeyCascade, ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.planing.models.operations import Operations, BaseOperationQuerySet

logger = logging.getLogger(__name__)


class Operation_valueQuerySet(BaseOperationQuerySet):
    def create(self, **kwargs):
        if kwargs.get('value') == 0:
            raise Exception('value must be not 0 !!!')

        return super().create(**kwargs)


class Operation_valueManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Operation_valueQuerySet(self.model, using=self._db)


class Operation_value(AuditModel):
    operation = ForeignKeyCascade(Operations)
    edizm = ForeignKeyProtect(Ed_izm, default=None)
    value = DecimalField(decimal_places=4, max_digits=19)
    props = BitField(flags=(
        ('perone', 'Из расчета на еденицу продукции'),
        ('used_in_start', 'Учавствовало в учете запуска'),
        ('used_in_release', 'Учавствовало в учете выпуска'),
    ), default=0, db_index=True)

    objects = Operation_valueManager()

    def __str__(self):
        return f"ID:{self.id}, \n" \
               f"value: {self.value}, \n" \
               f"props: {self.props}, \n" \
               f"edizm: [{self.edizm}]\n"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица значений операции'
