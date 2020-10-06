import logging

from django.contrib.postgres.fields import ArrayField
from django.db.models import DecimalField, BigIntegerField, TextField, BooleanField, DateTimeField, PositiveIntegerField

from isc_common.auth.models.user import User
from isc_common.datetime import DateTimeToStr
from isc_common.fields.code_field import CodeField, JSONFieldIVC
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.managers.common_manager import CommonManager
from isc_common.models.base_ref import Hierarcy
from kaf_pas.ckk.models.item import Item
from kaf_pas.planing.models.operation_types import Operation_types
from kaf_pas.planing.models.production_order import Production_orderQuerySet
from kaf_pas.production.models.launches import Launches

logger = logging.getLogger(__name__)


class Production_order_per_launchManager(CommonManager):

    def get_queryset(self):
        return Production_orderQuerySet(self.model, using=self._db)


class Production_order_per_launch(Hierarcy):
    from kaf_pas.planing.models.status_operation_types import Status_operation_types
    from kaf_pas.planing.models.operation_refs import Operation_refsManager

    arranges_exucutors = ArrayField(BigIntegerField(), default=list)
    cnt_opers = PositiveIntegerField()
    creator = ForeignKeyProtect(User, related_name='Production_order_per_launch_creator')
    date = DateTimeField(default=None)
    description = TextField(null=True, blank=True)
    demand_codes_str = CodeField()
    edizm_arr = ArrayField(CodeField(null=True, blank=True))
    exucutors = ArrayField(BigIntegerField(), default=list)
    isDeleted = BooleanField()
    isFolder = BooleanField(default=None)
    item = ForeignKeyProtect(Item, related_name='Production_order_per_launch_item')
    launch = ForeignKeyCascade(Launches)
    location_ids = ArrayField(BigIntegerField(), default=list)
    location_sector_ids = ArrayField(BigIntegerField(), default=list)
    location_sectors_full_name = ArrayField(TextField(), default=list)
    location_status_ids = JSONFieldIVC()
    location_statuses = JSONFieldIVC()
    location_status_colors = JSONFieldIVC()
    num = CodeField()
    opertype = ForeignKeyProtect(Operation_types, related_name='Production_order_per_launch_opertype')
    parent_item = ForeignKeyProtect(Item, null=True, blank=True, related_name='Production_order_per_launch_parent_item')
    props = Operation_refsManager.props()
    status = ForeignKeyProtect(Status_operation_types)
    value1_sum = DecimalField(decimal_places=4, max_digits=19)
    value_made = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    value_odd = DecimalField(decimal_places=4, max_digits=19)
    value_start = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    value_sum = DecimalField(decimal_places=4, max_digits=19)

    objects = Production_order_per_launchManager()

    # started_partly = Status_operation_types.objects.get(code='started_partly')
    # started = Status_operation_types.objects.get(code='started')

    def __str__(self):
        return f'id: {self.id}, ' \
               f'date: {DateTimeToStr(self.date)}, ' \
               f'num: {self.num}, ' \
               f'description: {self.description}, ' \
               f'opertype: [{self.opertype}], ' \
               f'creator: [{self.creator}], ' \
               f'exucutors: [{self.exucutors}], ' \
               f'status: [{self.status}], ' \
               f'launch: [{self.launch}], ' \
               f'edizm: [{self.edizm_arr}], ' \
               f'item: [{self.item}], ' \
               f'parent_item: [{self.parent_item}], ' \
               f'cnt_opers: {self.cnt_opers}, ' \
               f'value_sum: {self.value_sum},' \
               f'value1_sum: {self.value1_sum},' \
               f'value_start: {self.value_start},' \
               f'value_made: {self.value_made},' \
               f'value_odd: {self.value_odd}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Заказы на производство'
        managed = False
        # db_table = 'planing_production_order_per_launch_view'
        db_table = 'planing_production_order_per_launch_tbl'
