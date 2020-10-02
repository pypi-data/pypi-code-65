import logging

from django.db.models import TextField, BooleanField, DateTimeField, DecimalField

from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect, ForeignKeySetNull
from isc_common.models.base_ref import Hierarcy
from isc_common.models.standard_colors import Standard_colors
from isc_common.models.tree_audit import TreeAuditModelQuerySet, TreeAuditModelManager
from isc_common.number import DecimalToStr
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.planing.models.operation_operation import Operation_operation
from kaf_pas.planing.models.operation_refs import Operation_refsManager
from kaf_pas.planing.models.operation_types import Operation_types
from kaf_pas.planing.models.status_operation_types import Status_operation_types
from kaf_pas.production.models.launches import Launches
from kaf_pas.production.models.operations import Operations
from kaf_pas.production.models.resource import Resource

logger = logging.getLogger(__name__)


class Operations_viewQuerySet(TreeAuditModelQuerySet):
    pass


class Operations_viewManager(TreeAuditModelManager):

    @staticmethod
    def getRecord(record):
        res = {
            'creator_id': record.creator.id,
            'date': record.date,
            'description': record.description,
            'edizm__code': record.edizm.code if record.value and record.edizm else None,
            'edizm__name': record.edizm.name if record.value and record.edizm else None,
            'edizm_id': record.edizm.id if record.value and record.edizm else None,
            'id': record.id,
            'item__STMP_1__value_str': record.item.STMP_1.value_str if record.item and record.item.STMP_1 and record.item.STMP_1 else None,
            'item__STMP_1_id': record.item.STMP_1.id if record.item and record.item.STMP_1 and record.item.STMP_1 else None,
            'item__STMP_2__value_str': record.item.STMP_2.value_str if record.item and record.item.STMP_2 and record.item.STMP_2 else None,
            'item__STMP_2_id': record.item.STMP_2.id if record.item and record.item.STMP_2 and record.item.STMP_2 else None,
            'item_id': record.item.id if record.item else None,
            'item_item_name': record.item.item_name if record.item else None,
            'location__code': record.resource.location.code if record.resource and record.resource else None,
            'location__full_name': record.resource.location.full_name if record.resource and record.resource else None,
            'location__name': record.resource.location.name if record.resource and record.resource else None,
            'location_id': record.resource.location.id if record.resource else None,
            'num': record.num,
            'operation_operation_edizm__name': record.operation_operation.ed_izm.name if record.operation_operation and record.operation_operation.ed_izm else None,
            'operation_operation_edizm_id': record.operation_operationn.ed_izm.id if record.operation_operation and record.operation_operation.ed_izm else None,
            'operation_operation_id': record.operation_operation.id if record.operation_operation else None,
            'operation_operation_num': record.operation_operation.num if record.operation_operation else None,
            'operation_operation_qty': DecimalToStr(record.operation_operation.qty) if record.operation_operation else None,
            'opertype__full_name': record.opertype.full_name,
            'opertype_id': record.opertype.id,
            'parent_id': record.parent.id if record.parent else None,
            'production_operation__full_name': record.production_operation.full_name if record.production_operation else None,
            'production_operation__name': record.production_operation.name if record.production_operation else None,
            'resource__code': record.resource.code if record.resource and record.resource else None,
            'resource__description': record.resource.description if record.resource and record.resource else None,
            'resource__name': record.resource.name if record.resource and record.resource else None,
            'resource_fin__name': record.resource_fin.name if record.resource_fin and record.resource_fin else None,
            'resource_id': record.resource.id if record.resource else None,
            'status__code': record.status.code if record.status else None,
            'status__name': record.status.name if record.status else None,
            'status_id': record.status.id if record.status else None,
            # 'operation_level__code': record.level.code if record.level else None,
            # 'operation_level__name': record.level.name if record.level else None,
            # 'operation_level_id': record.level.id if record.level else None,
        }
        return res

    def get_queryset(self):
        return Operations_viewQuerySet(self.model, using=self._db)


class Operations_view(Hierarcy):
    # parent = ForeignKeyProtect("self", null=True, blank=True)
    # level = ForeignKeyProtect(Levels, null=True, blank=True)
    color = ForeignKeySetNull(Standard_colors, null=True, blank=True)
    creator = ForeignKeyProtect(User, related_name='Operations_view_creator')
    date = DateTimeField(default=None)
    description = TextField(null=True, blank=True)
    edizm = ForeignKeySetNull(Ed_izm, null=True, blank=True)
    isFolder = BooleanField(default=None)
    item = ForeignKeySetNull(Item, null=True, blank=True)
    launch = ForeignKeySetNull(Launches, null=True, blank=True)
    location = ForeignKeySetNull(Locations, null=True, blank=True)
    mark = CodeField()
    num = CodeField()
    operation_operation = ForeignKeySetNull(Operation_operation, null=True, blank=True)
    opertype = ForeignKeyProtect(Operation_types, related_name='Operations_view_opertype')
    production_operation = ForeignKeySetNull(Operations, null=True, blank=True)
    props = Operation_refsManager.props()
    resource = ForeignKeySetNull(Resource, null=True, blank=True)
    status = ForeignKeyProtect(Status_operation_types)
    value = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)

    objects = Operations_viewManager(alive_only=True)

    def __str__(self):
        try:
            return f"ID:{self.id}, \n" \
                   f"num:{self.num}, \n" \
                   f"creator: [{self.creator}], \n" \
                   f"date: {self.date}, \n" \
                   f"edizm: [{self.edizm}], \n" \
                   f"item: [{self.item}], \n" \
                   f"location: [{self.location}], \n" \
                   f"opertype: [{self.opertype}, \n" \
                   f"production_operation: [{self.production_operation}], \n" \
                   f"props: {self.props}, \n" \
                   f"launch: [{self.launch}], \n" \
                   f"resource: [{self.resource}], \n" \
                   f"status: [{self.status}], \n" \
                   f"value: {self.value}, \n" \
                   f"description: {self.description}, \n" \
                   f"parent_id: {self.parent}, \n"
        except Exception as ex:
            return str(ex)
        # return super().__str__()

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Опреации системные'
        managed = False
        db_table = 'planing_operations_view'
