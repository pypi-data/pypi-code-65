import logging

from django.db.models import PositiveIntegerField, BigIntegerField

from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.models.audit_history import AuditHistory, AuditHistoryManager, AuditHistoryQuerySet
from kaf_pas.ckk.models.item import Item, Item_add
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.kd.models.documents import Documents
from kaf_pas.kd.models.lotsman_documents_hierarcy import Lotsman_documents_hierarcy

logger = logging.getLogger(__name__)


class Item_historyQuerySet(AuditHistoryQuerySet):
    pass


class Item_historyManager(AuditHistoryManager):

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
        return Item_historyQuerySet(self.model, using=self._db)


class Item_history(AuditHistory):
    item = ForeignKeyCascade(Item)

    STMP_1 = ForeignKeyProtect(Document_attributes, related_name='Item_history_STMP_1', null=True, blank=True)
    STMP_2 = ForeignKeyProtect(Document_attributes, related_name='Item_history_STMP_2', null=True, blank=True)
    version = PositiveIntegerField(null=True, blank=True)

    props = Item_add.get_prop_field()

    document = ForeignKeyProtect(Documents, null=True, blank=True)
    lotsman_document = ForeignKeyProtect(Lotsman_documents_hierarcy, null=True, blank=True)
    lotsman_type_id = BigIntegerField(null=True, blank=True)

    objects = Item_historyManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'История операций'
