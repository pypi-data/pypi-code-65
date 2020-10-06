import logging

from bitfield import BitField
from django.db.models import TextField

from isc_common.fields.code_field import JSONFieldIVC
from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from kaf_pas.production.models.launches import Launches

logger = logging.getLogger(__name__)


class Launch_detailQuerySet(AuditQuerySet):
    def delete(self):
        super().delete()


class Launch_detailManager(AuditManager):

    @staticmethod
    def props():
        return BitField(flags=(
            ('production_order', 'Задания на производство'),  # 1
        ), db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'item_full_name': record.item_full_name,
            'notes': record.notes,
            'launch_id': record.ready.id,
            'ready__lastmodified': record.ready.lastmodified,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Launch_detailQuerySet(self.model, using=self._db)


class Launch_detail(AuditModel):
    launch = ForeignKeyCascade(Launches)
    item_full_name = TextField(null=True, blank=True)
    item_full_name_obj = JSONFieldIVC()
    notes = TextField(null=True, blank=True)
    props = Launch_detailManager.props()

    objects = Launch_detailManager()

    def __str__(self):
        return f"ID:{self.id}"

    class Meta:
        verbose_name = 'Детализация запусков'
