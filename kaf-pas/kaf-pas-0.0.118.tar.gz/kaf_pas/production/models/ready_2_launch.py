import logging

from bitfield import BitField
from django.db.models import TextField
from django.forms import model_to_dict

from isc_common import delAttr, setAttr
from isc_common.bit import TurnBitOn
from isc_common.fields.related import ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from isc_common.number import DelProps
from kaf_pas.ckk.models.item import Item
from kaf_pas.production.models.ready_2_launch_ext import Ready_2_launch_ext
from kaf_pas.sales.models.demand import Demand

logger = logging.getLogger(__name__)


class Ready_2_launchQuerySet(AuditQuerySet):
    def _del_options(self, request):
        from isc_common import delAttr

        delAttr(request.json.get('data'), 'full_name')
        delAttr(request.json.get('data'), 'check_qty')
        delAttr(request.json.get('data'), 'check_material')
        delAttr(request.json.get('data'), 'check_resources')
        delAttr(request.json.get('data'), 'check_edizm')
        delAttr(request.json.get('data'), 'check_operation')
        delAttr(request.json.get('data'), 'check_colvo')
        return request

    # ('check_qty', 'Проверять длительность'),  # 1
    # ('check_num', 'Проверять № п/п'),  # 2
    # ('check_material', 'Проверять материалы'),  # 4
    # ('check_resources', 'Проверять ресурсы'),  # 8
    # ('check_edizm', 'Проверять еденицу измерения'),  # 16
    # ('check_operation', 'Проверять операцию'),  # 32
    # ('check_colvo', 'Проверять количество'),  # 64

    def get_info(self, request, *args):
        request = DSRequest(request=request)
        request = self._del_options(request)
        criteria = self.get_criteria(json=request.json)
        cnt = super().filter(*args, criteria).count()
        cnt_all = super().filter().count()
        return dict(qty_rows=cnt, all_rows=cnt_all)

    def get_range_rows1(self, request, function=None, distinct_field_names=None):
        request = DSRequest(request=request)
        request = self._del_options(request)
        self.alive_only = request.alive_only
        self.enabledAll = request.enabledAll
        res = self.get_range_rows(start=request.startRow, end=request.endRow, function=function, distinct_field_names=distinct_field_names, json=request.json)
        return res


class Ready_2_launchManager(AuditManager):
    ready_2_launch_ext = Ready_2_launch_ext()

    def createFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()

        demand_ids = _data.get('demand')
        item_id = _data.get('item_id')

        delAttr(_data, 'demand__date')
        delAttr(_data, 'demand__name')
        delAttr(_data, 'demand__code')
        delAttr(_data, 'demand__description')
        delAttr(_data, 'item__STMP_1__value_str')
        delAttr(_data, 'item__STMP_2__value_str')
        delAttr(_data, 'item__STMP_1_id')
        delAttr(_data, 'item__STMP_2_id')
        delAttr(_data, 'item_id')

        props = 0
        if _data.get('check_qty'):
            props = TurnBitOn(props, 0)
        delAttr(_data, 'check_qty')

        if _data.get('check_num'):
            props = TurnBitOn(props, 1)
        delAttr(_data, 'check_num')

        if _data.get('check_material'):
            props = TurnBitOn(props, 2)
        delAttr(_data, 'check_material')

        if _data.get('check_resources'):
            props = TurnBitOn(props, 3)
        delAttr(_data, 'check_resources')

        if _data.get('check_edizm'):
            props = TurnBitOn(props, 4)
        delAttr(_data, 'check_edizm')

        if _data.get('check_operation'):
            props = TurnBitOn(props, 5)
        delAttr(_data, 'check_operation')

        if _data.get('check_colvo'):
            props = TurnBitOn(props, 6)
        delAttr(_data, 'check_colvo')

        setAttr(_data, 'props', props)

        delAttr(_data, 'date')

        if isinstance(demand_ids, list):
            for demand_id in demand_ids:
                demand = Demand.objects.get(id=demand_id)
                item = demand.precent_item.item
                delAttr(_data, 'demand')
                setAttr(_data, 'demand_id', demand_id)
                setAttr(_data, 'item_id', item.id)
                res = super().create(**_data)

                self.ready_2_launch_ext.make(
                    demand=demand,
                    user=request.user,
                    ready_2_launch=res,
                    props=props
                )

                res = Ready_2_launchManager.getRecord(res)
                data.update(DelProps(res))
        else:
            item = Item.objects.get(id=item_id)
            setAttr(_data, 'item', item)
            res = super().create(**_data)

            self.ready_2_launch_ext.make(
                item=item,
                user=request.user,
                ready_2_launch=res,
                props=props
            )

            res = Ready_2_launchManager.getRecord(res)
            data.update(DelProps(res))

        return data

    def reculcFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        ready_launtch_ids = data.get('data')

        for ready_launtch_id in ready_launtch_ids:
            _data = model_to_dict(Ready_2_launch.objects.get(id=ready_launtch_id))
            delAttr(_data, 'id')
            delAttr(_data, 'notes')
            setAttr(_data, 'demand_id', _data.get('demand'))
            setAttr(_data, 'item_id', _data.get('item'))
            delAttr(_data, 'demand')
            delAttr(_data, 'item')
            setAttr(_data, 'props', _data.get('props')._value)
            res = super().create(**_data)
            self.ready_2_launch_ext.make(
                demand=res.demand,
                item=res.item,
                user=request.user,
                ready_2_launch=res,
                props=_data.get('props')
            )

            res = Ready_2_launchManager.getRecord(res)
            res = DelProps(res)
        return res

    def updateFromRequest(self, request, removed=None, function=None):
        if not isinstance(request, DSRequest):
            request = DSRequest(request=request)
        data = request.get_data()
        return data

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'lastmodified': record.lastmodified,
            'demand_id': record.demand.id if record.demand else None,
            'demand__date': record.demand.date if record.demand else None,
            'demand__code': record.demand.code if record.demand else None,
            'demand__name': record.demand.name if record.demand else None,
            'demand__description': record.demand.description if record.demand else None,
            'check_qty': record.props.check_qty,
            'check_num': record.props.check_num,
            'check_material': record.props.check_material,
            'check_resources': record.props.check_resources,
            'check_edizm': record.props.check_edizm,
            'check_operation': record.props.check_operation,
            'check_colvo': record.props.check_colvo,
            'item_id': record.item.id,
            'item__STMP_1_id': record.item.STMP_1.id if record.item.STMP_1 is not None else None,
            'item__STMP_1__value_str': record.item.STMP_1.value_str if record.item.STMP_1 is not None else None,
            'item__STMP_2_id': record.item.STMP_2.id if record.item.STMP_2 is not None else None,
            'item__STMP_2__value_str': record.item.STMP_2.value_str if record.item.STMP_2 is not None else None,
            'notes': record.notes,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return DelProps(res)

    def get_queryset(self):
        return Ready_2_launchQuerySet(self.model, using=self._db)


class Ready_2_launch(AuditModel):
    demand = ForeignKeyCascade(Demand, null=True, blank=True)
    item = ForeignKeyCascade(Item)
    notes = TextField(null=True, blank=True)
    props = BitField(flags=(
        ('check_qty', 'Проверять длительность'),  # 1
        ('check_num', 'Проверять № п/п'),  # 2
        ('check_material', 'Проверять материалы'),  # 4
        ('check_resources', 'Проверять ресурсы'),  # 8
        ('check_edizm', 'Проверять еденицу измерения'),  # 16
        ('check_operation', 'Проверять операцию'),  # 32
        ('check_colvo', 'Проверять количество'),  # 64
    ), default=0, db_index=True)

    objects = Ready_2_launchManager()

    def __str__(self):
        return f"ID:{self.id}"

    class Meta:
        verbose_name = 'Готовность к запуску'
