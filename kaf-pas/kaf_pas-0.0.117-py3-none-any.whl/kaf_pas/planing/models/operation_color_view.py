import logging

from django.db.models import Model, DecimalField, DateTimeField, BigIntegerField

from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditManager, AuditQuerySet
from isc_common.models.standard_colors import Standard_colors
from isc_common.number import DecimalToStr
from kaf_pas.planing.models.operations import Operations
from kaf_pas.production.models.launches import Launches
from kaf_pas.sales.models.demand import Demand

logger = logging.getLogger(__name__)


class Operation_color_viewQuerySet(AuditQuerySet):
    def get_range_rows1(self, request, function=None, distinct_field_names=None, remove_fields=None):
        from kaf_pas.planing.models.production_order_opers import Production_order_opers

        request = DSRequest(request=request)
        data = request.get_data()

        records = data.get('records')
        parentId = data.get('parentId')

        res = []
        if isinstance(records, list) and len(records) > 0 and isinstance(parentId, int):
            record = records[0]

            prev = Production_order_opers.objects.filter(
                parent_id=parentId,
                deleted_at=None,
                production_operation_num=record.get('production_operation_num') - 1
            )

            if prev.count() > 0:
                prev = prev[0]
                if prev.production_operation_is_launched:
                    res = [Operation_color_viewManager.getRecord(record) for record in Operation_color_view.objects.filter(operation_id=prev.id)]

        if len(res) == 0:
            res = list(map(lambda x: dict(
                demand_id=None,
                demand__code=None,
                demand__date=None,
                launch_id=None,
                launch__code=None,
                launch__date=None,
                id=x.id,
                color_id=x.id,
                color__color=x.color,
                color__code=x.code,
                color__name=x.name,
                summa=None
            ), Standard_colors.objects.all()))

        return res


class Operation_color_viewManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'demand_id': record.demand.id if record.demand else None,
            'demand__code': record.demand.code if record.demand else None,
            'demand__date': record.demand.date if record.demand else None,
            'launch_id': record.launch.id if record.launch else None,
            'launch__code': record.launch.code if record.launch else None,
            'launch__date': record.launch.date if record.launch else None,
            'color_id': record.color.id,
            'color__color': record.color.color,
            'color__name': record.color.name,
            'summa': DecimalToStr(record.summa),
        }
        return res

    def get_queryset(self):
        return Operation_color_viewQuerySet(self.model, using=self._db)


class Operation_color_view(Model):
    id = BigIntegerField(primary_key=True)
    deleted_at = DateTimeField(null=True, blank=True)
    launch = ForeignKeyProtect(Launches, null=True, blank=True)
    demand = ForeignKeyProtect(Demand, null=True, blank=True)
    color = ForeignKeyProtect(Standard_colors)
    operation = ForeignKeyProtect(Operations)
    summa = DecimalField(decimal_places=4, max_digits=19)

    objects = Operation_color_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        managed = False
        db_table = 'planing_operation_color_view'
        verbose_name = 'Цвета операций'
