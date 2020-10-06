import logging

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import EmptyResultSet
from django.db import transaction
from django.db.models import DecimalField, DateTimeField, TextField, PositiveIntegerField, BigIntegerField, BooleanField, SmallIntegerField

from isc_common import delAttr
from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect, ForeignKeySetNull
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_manager import CommonQuerySet, CommonManager
from isc_common.models.audit import AuditModel
from isc_common.models.standard_colors import Standard_colors
from isc_common.number import DelProps, DecimalToStr
from isc_common.ws.webSocket import WebSocket
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.ckk.models.locations_users import Locations_users
from kaf_pas.planing.models.operation_operation import Operation_operation
from kaf_pas.planing.models.operation_types import Operation_types
from kaf_pas.planing.models.production_ext import Production_ext
from kaf_pas.production.models.launches import Launches
from kaf_pas.production.models.operations import Operations
from kaf_pas.production.models.resource import Resource

logger = logging.getLogger(__name__)


class Production_order_opersQuerySet(CommonQuerySet):
    # def value_odd(self):
    #     for this in self:
    #         return ToDecimal(this.value_odd)
    #     return 0
    #
    # def value_odd_ship(self):
    #     for this in self:
    #         return ToDecimal(this.value_odd_ship)
    #     return 0

    def get_range_rows(self, start=None, end=None, function=None, json=None, distinct_field_names=None, user=None, *args, **kwargs):
        child_launch_id = json.get('data').get('child_launch_id')
        if child_launch_id and child_launch_id == json.get('data').get('launch_id'):
            child_launch_id = None

        delAttr(json.get('data'), 'child_launch_id')
        queryResult = self._get_range_rows(*args, start=start, end=end, function=function, json=json, distinct_field_names=distinct_field_names)

        try:
            logger.debug(f'\n\n{queryResult.query}\n')
        except EmptyResultSet:
            pass

        res = [function(record, user) for record in queryResult]
        return res


class Production_order_opersManager(CommonManager):
    @staticmethod
    def getRecord(record, user=None):
        from kaf_pas.production.models.operation_executor import Operation_executor

        if user is None:
            enabled = False
        else:
            users_ids = [operation.user_id for operation in Operation_executor.objects.filter(operation_id=record.production_operation_id)]
            if len(users_ids) > 0:
                enabled = user.is_develop or user.is_admin or user.id in users_ids
            else:
                location_ids = [location_user.location.id for location_user in Locations_users.objects.filter(user_id=user)]
                enabled = user.is_develop or user.is_admin or record.resource.location.id in location_ids if record.resource else False

        res = {
            # 'location_sector_id': record.location_sector.id,
            'creator__short_name': record.creator.get_short_name,
            'date': record.date,
            'production_operation_is_absorption': record.production_operation_is_absorption,
            'parent_id': record.parent_id,
            'description': record.description,
            'edizm__name': ' / '.join(record.edizm_arr) if record.edizm_arr is not None else None,
            'enabled': enabled,
            'id': record.id,
            'item_id': record.item.id,
            'launch_id': record.launch.id,
            'location_id': record.location.id,
            'location__code': record.location.code,
            'location__full_name': record.location.full_name,
            'location__name': record.location.name,
            'location_fin_id': record.location_fin.id if record.location_fin else None,
            'location_fin__code': record.location_fin.code if record.location_fin else None,
            'location_fin__full_name': record.location_fin.full_name if record.location_fin else None,
            'location_fin__name': record.location_fin.name if record.location_fin else None,
            'num': record.id,
            'production_operation__full_name': record.operation_operation.production_operation.full_name if record.operation_operation else None,
            'production_operation__name': record.operation_operation.production_operation.name if record.operation_operation else None,
            'production_operation_attrs': record.production_operation_attrs,
            'production_operation_colors': record.production_operation_colors,
            'production_operation_edizm__name': record.operation_operation.ed_izm.name if record.operation_operation and record.operation_operation.ed_izm else None,
            'production_operation_edizm_id': record.operation_operation.ed_izm.id if record.operation_operation and record.operation_operation.ed_izm else None,

            'production_operation_color_id': record.production_operation_color.id if record.production_operation_color and record.production_operation_color else None,
            'production_operation_color__name': record.production_operation_color.name if record.production_operation_color and record.production_operation_color else None,
            'production_operation_color__color': record.production_operation_color.color if record.production_operation_color and record.production_operation_color else None,

            'production_operation_id': record.operation_operation.production_operation.id if record.operation_operation else None,
            'production_operation_num': record.operation_operation.num if record.operation_operation else None,
            'production_operation_qty': record.operation_operation.qty if record.operation_operation else None,
            'resource__code': record.resource.code,
            'resource__description': record.resource.description,
            'resource__name': record.resource.name,
            'resource_id': record.resource.id,
            'resource_fin__code': record.resource_fin.code if record.resource_fin is not None else None,
            'resource_fin__description': record.resource_fin.description if record.resource_fin is not None else None,
            'resource_fin__name': record.resource_fin.name if record.resource_fin is not None else None,
            'resource_fin_id': record.resource_fin.id if record.resource_fin is not None else None,
            'value_sum': DecimalToStr(record.value_sum),
            'value_made': DecimalToStr(record.value_made),
            'value_odd': DecimalToStr(record.value_odd),
            'value_ship': DecimalToStr(record.value_ship),
            'value_odd_ship': DecimalToStr(record.value_odd_ship),
            'value1_sum': DecimalToStr(record.value1_sum),
            # 'value1_sum_len': len(record.value1_sum),
            'value_start': DecimalToStr(record.value_start),
            'isDeleted': record.isDeleted,
            'production_operation_is_transportation': record.production_operation_is_transportation,
            'production_operation_is_launched': record.production_operation_is_launched,
            'production_operation_is_grouped': record.production_operation_is_grouped,
        }
        return DelProps(res)

    @staticmethod
    def refreshRows(ids, user):
        from kaf_pas.planing.models.production_order import Production_orderManager

        if ids is None:
            return

        ids = Production_orderManager.ids_list_2_int_list(ids)
        records = [Production_order_opersManager.getRecord(record, user) for record in Production_order_opers.objects.filter(id__in=ids)]
        WebSocket.row_refresh_grid(grid_id=settings.GRID_CONSTANTS.refresh_operationsGrid_row, records=records)

    @staticmethod
    def fullRows(suffix=''):
        WebSocket.full_refresh_grid(grid_id=f'{settings.GRID_CONSTANTS.refresh_operationsGrid}{suffix}')

    def createFromRequest(self, request):
        # raise NotImplement()

        request = DSRequest(request=request)
        production_ext = Production_ext()

        data = request.get_data()

        production_ext.update_operation(data=data, user=request.user)

        return data

    def deleteFromRequest(self, request):
        request = DSRequest(request=request)
        # raise NotImplement()
        ids = request.get_old_ids()
        res = 0
        production_ext = Production_ext()

        with transaction.atomic():
            production_ext.delete_operation(ids=ids, user=request.user)

        return res

    def updateFromRequest(self, request):
        request = DSRequest(request=request)
        # raise NotImplement()
        production_ext = Production_ext()

        data = request.get_data()
        old_data = request.get_oldValues()

        return production_ext.update_operation(data=data, old_data=old_data, user=request.user)

    def get_queryset(self):
        return Production_order_opersQuerySet(self.model, using=self._db)


class Production_order_opers(AuditModel):
    from kaf_pas.planing.models.status_operation_types import Status_operation_types
    from kaf_pas.planing.models.operation_refs import Operation_refsManager

    creator = ForeignKeyProtect(User, related_name='Production_order_opers_creator')
    date = DateTimeField(default=None)
    description = TextField(null=True, blank=True)
    edizm_arr = ArrayField(CodeField(null=True, blank=True))
    isDeleted = BooleanField()
    item = ForeignKeyProtect(Item)
    launch = ForeignKeyProtect(Launches)
    location = ForeignKeyProtect(Locations, related_name='Production_order_opers_location')
    location_fin = ForeignKeySetNull(Locations, related_name='Production_order_opers_location_fin', null=True, blank=True)
    num = CodeField()
    operation_operation = ForeignKeySetNull(Operation_operation, null=True, blank=True)
    operation_operation_num = PositiveIntegerField()
    opertype = ForeignKeyProtect(Operation_types, related_name='Production_order_opers_opertype')
    parent_id = BigIntegerField()
    production_operation = ForeignKeyProtect(Operations)
    production_operation_attrs = ArrayField(CodeField(null=True, blank=True))
    production_operation_color = ForeignKeyProtect(Standard_colors, null=True, blank=True)
    production_operation_colors = ArrayField(SmallIntegerField(null=True, blank=True))
    production_operation_edizm = ForeignKeyProtect(Ed_izm, null=True, blank=True)
    production_operation_is_absorption = BooleanField()
    production_operation_is_grouped = BooleanField()
    production_operation_is_launched = BooleanField()
    production_operation_is_transportation = BooleanField()
    production_operation_num = PositiveIntegerField()
    resource = ForeignKeyProtect(Resource, related_name='Production_order_opers_resource')
    resource_fin = ForeignKeyProtect(Resource, null=True, blank=True, related_name='Production_order_opers_resource_fin')
    status = ForeignKeyProtect(Status_operation_types)
    value1_sum = ArrayField(DecimalField(decimal_places=4, max_digits=19))
    value_made = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    value_odd = DecimalField(decimal_places=4, max_digits=19)
    value_odd_ship = DecimalField(decimal_places=4, max_digits=19)
    value_ship = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    value_start = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    value_sum = DecimalField(decimal_places=4, max_digits=19)

    props = Operation_refsManager.props()

    objects = Production_order_opersManager()

    @property
    def this(self):
        from kaf_pas.planing.models.operations import Operations
        return Operations.objects.get(id=self.id)

    @property
    def parent(self):
        from kaf_pas.planing.models.production_order import Production_order
        return Production_order.objects.get(id=self.parent_id)

    @property
    def left_neighbour(self):
        if self.production_operation_num == 1:
            return None

        return self.all_childs[self.production_operation_num - 2]

    @property
    def right_neighbour(self):
        if self.production_operation_num == len(self.all_childs):
            return None
        return self.all_childs[self.production_operation_num]

    @property
    def minus_operations(self):
        from kaf_pas.planing.models.production_order_values import Production_order_values
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.operation_typesStack import MADE_OPRS_MNS_TSK

        ids = map(lambda x: x.child, Operation_refs.objects.filter(parent_id=self.id, child__opertype__code=MADE_OPRS_MNS_TSK))
        return Production_order_values.objects.filter(operation__in=ids).alive()

    @property
    def plus_operations(self):
        from kaf_pas.planing.models.production_order_values import Production_order_values
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.operation_typesStack import MADE_OPRS_PLS_TSK

        ids = map(lambda x: x.child, Operation_refs.objects.filter(parent_id=self.id, child__opertype__code=MADE_OPRS_PLS_TSK))
        return Production_order_values.objects.filter(operation__in=ids).alive()

    @property
    def plus_grouped_operations(self):
        from kaf_pas.planing.models.production_order_values import Production_order_values
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.operation_typesStack import GROUP_TSK

        ids = map(lambda x: x.child, Operation_refs.objects.filter(parent_id=self.id, child__opertype__code=GROUP_TSK))
        return Production_order_values.objects.filter(operation__in=ids).alive()

    @property
    def has_moving_operations(self):
        return len(self.minus_operations) > 0 or len(self.plus_operations) or len(self.plus_grouping_operations) > 0

    @property
    def plus_grouping_operations(self):
        from kaf_pas.planing.models.production_order_values import Production_order_values
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.operation_typesStack import MADE_OPRS_PLS_GRP_TSK

        ids = list(map(lambda x: x.child, Operation_refs.objects.filter(parent_id=self.id, child__opertype__code=MADE_OPRS_PLS_GRP_TSK)))
        return Production_order_values.objects.filter(operation__in=ids).alive()

    @property
    def all_childs(self):
        return Production_order_opers.objects.filter(parent_id=self.parent_id).alive().order_by('production_operation_num')

    def __str__(self):
        return f'ID: {self.id}, production_operation: [{self.production_operation}]'

    def __repr__(self):
        return self.__str__()

    class Meta:
        managed = False
        db_table = 'planing_production_order_opers_view'
        verbose_name = 'Операции Заказа на производство'
