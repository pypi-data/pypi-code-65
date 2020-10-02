import logging

from django.conf import settings
from django.db.models import DecimalField, BooleanField

from isc_common import Wrapper, delAttr, setAttr
from isc_common.auth.models.user import User
from isc_common.common import blinkString, red, green, blue
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyCascade, ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditManager, AuditModel, AuditQuerySet
from isc_common.models.standard_colors import Standard_colors
from isc_common.number import DelProps, ToInt, DecimalToStr
from isc_common.ws.webSocket import WebSocket
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.locations import Locations
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.planing.models.operations import Operations
from kaf_pas.production.models.launches import Launches
from kaf_pas.production.models.resource import Resource
from kaf_pas.sales.models.demand import Demand

logger = logging.getLogger(__name__)


class Tmp_operation_value_viewQuerySet(AuditQuerySet):

    def get_range_rows1(self, request, function=None, distinct_field_names=None, remove_fields=None):
        from kaf_pas.production.models.launch_item_refs import Launch_item_refs
        from kaf_pas.planing.models.tmp_operation_value import Tmp_operation_value

        request = DSRequest(request=request)
        data = request.get_data()

        launch_id = data.get('launch_id', 0)
        item_id = data.get('item_id', 0)
        value = data.get('value', 0)

        delAttr(data, 'operationRecord')
        delAttr(data, 'item_id')
        delAttr(data, 'value')
        setAttr(data, 'user_id', request.user.id)

        request.set_data(data)

        items_query = Launch_item_refs.tree_objects.get_descendants(
            id=item_id,
            where_clause=f'where launch_id={launch_id}',
            include_self=True,
            distinct='distinct',
            order_by_clause='order by level'
        )

        # deleted = Tmp_operation_value.objects.filter(main_id=item_id, launch_id=launch_id, user=request.user).delete()
        # logger.debug(f'deleted: {deleted}')
        deleted1 = Tmp_operation_value.objects.filter(user=request.user, launch_id=launch_id).exclude(child_id__in=map(lambda x: x.child_id, items_query)).delete()
        deleted2 = Tmp_operation_value.objects.filter(user=request.user, launch_id=launch_id).exclude(parent_id__in=map(lambda x: x.parent_id, items_query)).delete()

        for item in items_query:
            res, _ = Tmp_operation_value.objects.update_or_create(
                parent=item.parent,
                main_id=item_id,
                child=item.child,
                launch=item.launch,
                user=request.user,
                deliting=False,
                editing=False,
                defaults=dict(value=value)
            )
            logger.debug(f'res: {res}')
        # break

        self.alive_only = request.alive_only
        self.enabledAll = request.enabledAll

        res = self.get_range_rows(
            start=request.startRow,
            end=request.endRow,
            function=function,
            distinct_field_names=distinct_field_names,
            json=request.json,
            criteria=request.get_criteria(),
            user=request.user
        )
        return res


class TMOV_Wrapper(Wrapper):
    isFolder = False
    pass


class Tmp_operation_value_viewManager(AuditManager):

    @staticmethod
    def fullRows(suffix=''):
        WebSocket.full_refresh_grid(grid_id=f'{settings.GRID_CONSTANTS.tmp_operation_value_view_grid}{suffix}')

    @staticmethod
    def refreshRows(ids):
        if isinstance(ids, int):
            ids = [ids]

        records = [Tmp_operation_value_viewManager.getRecord(record) for record in Tmp_operation_value_view.objects.filter(id__in=ids)]
        WebSocket.row_refresh_grid(grid_id=settings.GRID_CONSTANTS.tmp_operation_value_view_grid_row, records=records)

    @staticmethod
    def getRecord(record):
        from kaf_pas.ckk.models.item_line import Item_lineManager
        value_odd = record.value_odd
        if value_odd is not None and record.enabled == True:
            value_need = record.value
            if value_odd >= value_need:
                value_odd = blinkString(DecimalToStr(value_odd), blink=False, color=green, bold=True)
            else:
                value_odd = f'{blinkString(DecimalToStr(value_odd), blink=False, color=green, bold=True)} {blinkString(DecimalToStr(value_odd - value_need), blink=True, color=red, bold=True)}'
        else:
            value_odd = DecimalToStr(value_odd)

        res = {
            'id': record.id,
            'parent_id': record.parent.id if record.parent else None,
            'editing': record.editing,
            'deliting': record.deliting,
            'color__color': record.color.color if record.color else None,
            'color__name': record.color.name if record.color else None,
            'color_id': record.color.id if record.color else None,
            'demand__code': record.demand.code if record.demand else None,
            'demand__date': record.demand.date if record.demand else None,
            'demand_id': record.demand.id if record.demand else None,
            'edizm__code': record.edizm.code if record.edizm else None,
            'edizm__name': record.edizm.name if record.edizm else None,
            'edizm_id': record.edizm.id if record.edizm else None,
            'STMP_1__value_str': record.STMP_1.value_str if record.STMP_1 else None,
            'STMP_1_id': record.STMP_1.id if record.STMP_1 else None,
            'STMP_2__value_str': record.STMP_2.value_str if record.STMP_2 else None,
            'STMP_2_id': record.STMP_2.id if record.STMP_2 else None,
            'launch__code': record.launch.code if record.launch else None,
            'launch__date': record.launch.date if record.launch else None,
            'launch_id': record.launch.id if record.launch else None,
            'location__code': record.location.code if record.location else None,
            'location__full_name': record.location.full_name if record.location else None,
            'location__name': record.location.name if record.location else None,
            'location_id': record.location.id if record.location else None,
            'resource__code': record.resource.code if record.resource else None,
            'resource__name': record.resource.name if record.resource else None,
            'resource_id': record.resource.id if record.resource else None,
            'icon': Item_lineManager.getIcon(record),
            'value_sum': ToInt(record.value_sum),
            'value_odd': value_odd,
            'value_odd_real': record.value_odd,
            'value1_sum': blinkString(DecimalToStr(record.value1_sum), blink=False, color=blue, bold=True) if record.enabled == True else DecimalToStr(record.value1_sum),
            'value': ToInt(record.value),
            'enabled': record.enabled,
            'assembled': record.assembled,
        }

        return DelProps(res)

    def get_queryset(self):
        return Tmp_operation_value_viewQuerySet(self.model, using=self._db)


class Tmp_operation_value_view(AuditModel):
    color = ForeignKeyCascade(Standard_colors, null=True, blank=True)
    demand = ForeignKeyCascade(Demand, null=True, blank=True)
    edizm = ForeignKeyCascade(Ed_izm, null=True, blank=True)
    parent = ForeignKeyCascade(Item, null=True, blank=True, related_name='Tmp_operation_value_view_parent')
    launch = ForeignKeyCascade(Launches)
    item = ForeignKeyCascade(Item, null=True, blank=True)
    location = ForeignKeyCascade(Locations, null=True, blank=True)
    resource = ForeignKeyCascade(Resource, null=True, blank=True)
    last_tech_operation = ForeignKeyCascade(Operations)
    value_sum = DecimalField(verbose_name="Количество по документации", decimal_places=4, max_digits=19)
    value_odd = DecimalField(verbose_name="Количество Остаток", decimal_places=4, max_digits=19, null=True, blank=True)
    value1_sum = DecimalField(verbose_name="Количество на еденицу продукции", decimal_places=4, max_digits=19)
    section = CodeField(null=True, blank=True)
    isFolder = BooleanField()
    enabled = BooleanField()
    assembled = BooleanField()
    STMP_1 = ForeignKeyProtect(Document_attributes, verbose_name='Наименование изделия', related_name='STMP_1_Tmp_operation_value_view', null=True, blank=True)
    STMP_2 = ForeignKeyProtect(Document_attributes, verbose_name='Обозначение изделия', related_name='STMP_2_Tmp_operation_value_view', null=True, blank=True)
    user = ForeignKeyCascade(User)
    value = DecimalField(verbose_name="Кроличество на комплектацию введенное в ручную", max_digits=19, decimal_places=4, null=True, blank=True)

    objects = Tmp_operation_value_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Временное хранилище для занесения выполнения'
        managed = False
        db_table = 'planing_tmp_operation_value_view'
