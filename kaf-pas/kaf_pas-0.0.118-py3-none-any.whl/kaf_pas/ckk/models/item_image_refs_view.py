import logging

from django.db.models import BooleanField, TextField

from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel, AuditManager
from kaf_pas.ckk.models.item import Item
from kaf_pas.kd.models.documents_thumb import Documents_thumb
from kaf_pas.kd.models.documents_thumb10 import Documents_thumb10

logger = logging.getLogger(__name__)


class Item_image_refs_viewManager(AuditManager):
    @staticmethod
    def getRecord(record):
        res = {
            "id": record.thumb.id if record.thumb else None,
            "item_id": record.item.id,
            "path": record.thumb.path if record.thumb else None,
            "file_document": record.file_document,
            "prompt": record.file_document,
            "file_document_thumb_url": f'/logic/DocumentsThumb/Download/{record.thumb.id}/' if record.thumb else None,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res


class Item_image_refs_view(AuditModel):
    item = ForeignKeyCascade(Item)
    thumb = ForeignKeyCascade(Documents_thumb, null=True, blank=True)
    thumb10 = ForeignKeyCascade(Documents_thumb10, null=True, blank=True)
    useinprint = BooleanField()
    file_document = TextField()

    objects = Item_image_refs_viewManager()

    def __str__(self):
        return f"item: {self.item}, thumb: {self.thumb}, thumb10: {self.thumb10}"

    class Meta:
        verbose_name = 'Графические элементы'
        managed = False
        db_table = 'ckk_item_image_refs_view'
