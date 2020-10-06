import logging

from django.db.models import DecimalField, TextField

from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.base_ref import Hierarcy
from kaf_pas.planing.models.operation_types import Operation_types
from kaf_pas.planing.models.status_operation_types import Status_operation_types
from kaf_pas.production.models.launches import Launches

logger = logging.getLogger(__name__)


class Production_order_detail(Hierarcy):
    num = CodeField()
    description = TextField(null=True, blank=True)

    opertype = ForeignKeyProtect(Operation_types, related_name='Production_order_detail_opertype')
    creator = ForeignKeyProtect(User, related_name='Production_order_detail_creator')
    parent_launch = ForeignKeyProtect(Launches, related_name='Production_order_detail_parent_launch_id')
    launch = ForeignKeyProtect(Launches, related_name='Production_order_detail_child_launch_id')
    status = ForeignKeyProtect(Status_operation_types)
    # edizm = ForeignKeyProtect(Ed_izm)

    value_sum = DecimalField(decimal_places=4, max_digits=19)
    value_sum_common = DecimalField(decimal_places=4, max_digits=19)
    value1_sum = DecimalField(decimal_places=4, max_digits=19)
    value_start = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    value_made = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    value_made_common = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    value_odd = DecimalField(decimal_places=4, max_digits=19)
    value_odd_common = DecimalField(decimal_places=4, max_digits=19)

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return self.__str__()

    class Meta:
        managed = False
        db_table = 'planing_production_order_detail_view'
        verbose_name = 'Детализация Заданий на производство в разрезе запусков'
