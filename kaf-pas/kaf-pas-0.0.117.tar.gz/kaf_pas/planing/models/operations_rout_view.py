import logging

from django.db.models import TextField, BooleanField, DateTimeField, PositiveIntegerField, DecimalField, BigIntegerField

from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.base_ref import Hierarcy
from isc_common.models.tree_audit import TreeAuditModelQuerySet, TreeAuditModelManager
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.planing.models.levels import Levels
from kaf_pas.planing.models.operation_refs import Operation_refsManager
from kaf_pas.production.models.operations import Operations
from kaf_pas.production.models.resource import Resource

logger = logging.getLogger(__name__)


class Operations_rout_viewQuerySet(TreeAuditModelQuerySet):
    pass


class Operations_rout_viewManager(TreeAuditModelManager):

    @staticmethod
    def getRecord(record):
        location = Locations.objects.get(id=record.location_id)
        res = {
            'item__STMP_1__value_str': record.item__STMP_1_value_str,
            'item__STMP_2__value_str': record.item__STMP_2_value_str,
            'production_operation__full_name': Operations.objects.get(id=record.production_operation_id).full_name,
            'production_operation_num': record.production_operation_num,
            'production_operation_qty': record.production_operation_qty,
            'production_operation_edizm__name': Ed_izm.objects.get(id=record.production_operation_ed_izm_id).name if record.production_operation_ed_izm_id else None,
            'operation_level_name': Levels.objects.get(id=record.level_id).name,
            'mark': record.mark,
            'location__code': location.code,
            'location__full_name': location.full_name,
            'resource__name': Resource.objects.get(id=record.resource_id).name,
            'item_id': record.item_id,
            'level_id': record.level_id,
            'launch_id': record.launch_id,
            'location_id': record.location_id,
            'resource_id': record.resource_id,
            'id': record.id,
        }
        return res

    def get_queryset(self):
        return Operations_rout_viewQuerySet(self.model, using=self._db)


class Operations_rout_view(Hierarcy):
    date = DateTimeField(default=None)
    description = TextField(null=True, blank=True)
    opertype = ForeignKeyProtect(User, related_name='Operations_rout_view_opertype')
    creator = ForeignKeyProtect(User, related_name='Operations_rout_view_creator')
    STMP_1 = ForeignKeyProtect(Document_attributes, related_name='Operations_rout_view_STMP_1', null=True, blank=True)
    STMP_2 = ForeignKeyProtect(Document_attributes, related_name='Operations_rout_view_STMP_2', null=True, blank=True)
    production_operation = ForeignKeyProtect(Operations, related_name='Operations_rout_view_production_operation')
    item = ForeignKeyProtect(Item, related_name='Operations_rout_view_item1')
    isFolder = BooleanField(default=None)
    mark = CodeField()
    num = CodeField()
    item_STMP_1_value_str = NameField()
    item_TMP_2_value_str = NameField()
    level_id = BigIntegerField()
    location_id = BigIntegerField()
    resource_id = BigIntegerField()
    launch_id = BigIntegerField()
    production_operation_ed_izm_id = BigIntegerField(null=True, blank=True)
    production_operation_edizm = ForeignKeyProtect(Ed_izm, related_name='Operations_rout_view_ed_izm')
    production_operation_num = PositiveIntegerField(null=True, blank=True)
    production_operation_qty = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    props = Operation_refsManager.props()

    objects = Operations_rout_viewManager()

    def __str__(self):
        return f"ID:{self.id}, \n" \
               f"num:{self.num}, \n" \
               f"creator: [{self.creator}], \n" \
               f"date: {self.date}, \n" \
               f"description: {self.description}, \n" \
               f"parent_id: {self.parent}, \n"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Опреации системные'
        managed = False
        db_table = 'planing_operation_rout_view'
