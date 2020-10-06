import logging

from bitfield import BitField
from django.db import transaction
from django.db.models import DecimalField, UniqueConstraint, Q

from isc_common import Wrapper
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditManager, AuditQuerySet, AuditModel
from isc_common.models.standard_colors import Standard_colors
from isc_common.number import DelProps, ToDecimal
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.item import Item
from kaf_pas.planing.models.operations import Operations
from kaf_pas.production.models.launches import Launches
from kaf_pas.production.models.resource import Resource

logger = logging.getLogger(__name__)


class Tmp_operation_valueQuerySet(AuditQuerySet):
    pass


class TMPOWrapper(Wrapper):
    assembled = None
    child = None
    color = None
    color_id = None
    edizm = None
    edizm_id = None
    id = None
    isFolder = None
    last_tech_operation = None
    last_tech_operation_id = None
    launch = None
    launch_id = None
    parent = None
    parent_id = None
    resource = None
    resource_id = None
    value = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if isinstance(self.launch_id, int):
            self.launch = Launches.objects.get(id=self.launch_id)

        if isinstance(self.last_tech_operation_id, int):
            self.last_tech_operation = Operations.objects.get(id=self.last_tech_operation_id)

        if isinstance(self.resource_id, int):
            self.resource = Resource.objects.get(id=self.resource_id)

        if isinstance(self.resource_id, int):
            self.resource = Resource.objects.get(id=self.resource_id)

        if isinstance(self.color_id, int):
            self.color = Standard_colors.objects.get(id=self.color_id)

        if isinstance(self.edizm_id, int):
            self.edizm = Ed_izm.objects.get(id=self.edizm_id)

        if isinstance(self.id, int):
            self.child = Item.objects.get(id=self.id)

        if isinstance(self.parent_id, int):
            self.parent = Item.objects.get(id=self.parent_id)


class Tmp_operation_valueManager(AuditManager):

    @staticmethod
    def props():
        return BitField(flags=(
            ('enabled', 'Доступно'),  # 1
        ), db_index=True, default=1)

    def updateFromRequest(self, request, removed=None, function=None):
        from kaf_pas.planing.models.tmp_operation_value_view import Tmp_operation_value_view
        from kaf_pas.planing.models.tmp_operation_value_view import Tmp_operation_value_viewManager
        from kaf_pas.ckk.models.item_refs import Item_refs
        from kaf_pas.production.models.launch_item_refs import Launch_item_refs
        from sheduler import make_shedurer_tasks

        request = DSRequest(request=request)
        _data = request.get_data()
        data = request.get_data_wrapped(cls=TMPOWrapper)
        old_data = request.get_old_data_wrapped(cls=TMPOWrapper)

        if data.isFolder is None and data.assembled == True:
            make_shedurer_tasks(lambda: Tmp_operation_value_viewManager.refreshRows(data.id), when='1s')
            raise Exception(f'{data.child.item_name} не является сборочной единицей.')

        if data.value_odd_real == 0:
            make_shedurer_tasks(lambda: Tmp_operation_value_viewManager.refreshRows(data.id), when='1s')
            raise Exception(f'На {data.child.item_name} нет остатков.')

        with transaction.atomic():
            first_step = True
            for updated_row in super().filter(
                child=data.child,
                parent=data.parent,
                launch=data.launch,
                user=request.user):

                if first_step == False:
                    updated_row.delete()
                    continue

                updated_row.need_value=data.value
                updated_row.save()
                first_step = False

                if data.assembled != old_data.assembled:
                    for item_refs in Item_refs.objects.filter(child=data.child, parent=data.parent, props=Item_refs.props.relevant):
                        if data.assembled == True:
                            item_refs.props |= Item_refs.props.assembled
                            item_refs.save()
                        elif data.assembled == False:
                            item_refs.props &= ~Item_refs.props.assembled
                            item_refs.save()

                    for items_lower_levels in Launch_item_refs.tree_objects.get_descendants(
                            id=data.child.id,
                            where_clause=f'where launch_id={data.launch_id}',
                            include_self=False,
                            distinct='distinct'
                    ):
                        for updated_item in super().filter(
                                child=items_lower_levels.child,
                                parent=items_lower_levels.parent,
                                launch=data.launch,
                                user=request.user):

                            updated_item.need_value = None
                            if data.assembled == True:
                                updated_item.props &= ~Tmp_operation_value.props.enabled
                            elif data.assembled == False:
                                updated_item.props |= Tmp_operation_value.props.enabled
                            updated_item.save()

                            Tmp_operation_value_viewManager.refreshRows(updated_item.child.id)

                # res = Tmp_operation_value_viewManager.getRecord(updated_row)
            return _data

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'parent': record.parent.id if record.parent else None,
            'editing': record.editing,
            'deliting': record.deliting,
            'launch__code': record.launch.code if record.launch else None,
            'launch__date': record.launch.date if record.launch else None,
            'launch_id': record.launch.id if record.launch else None,
        }
        return DelProps(res)

    def get_queryset(self):
        return Tmp_operation_valueQuerySet(self.model, using=self._db)


class Tmp_operation_value(AuditModel):
    child = ForeignKeyCascade(Item, related_name='Tmp_operation_value_child')
    parent = ForeignKeyCascade(Item, related_name='Tmp_operation_value_parent', null=True, blank=True)
    main = ForeignKeyCascade(Item, related_name='Tmp_operation_value_main')
    launch = ForeignKeyCascade(Launches, null=True, blank=True)
    user = ForeignKeyCascade(User)
    value = DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    need_value = DecimalField(max_digits=19, decimal_places=4, null=True, blank=True)
    props = Tmp_operation_valueManager.props()
    # info = JSONFieldIVC()

    objects = Tmp_operation_valueManager()

    def __str__(self):
        return f'ID:{self.id}, child: [{self.child}], parent: [{self.parent}], launch: [{self.launch}], user: [{self.user}]'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Временное хранилище для занесения выполнения'
        constraints = [
            UniqueConstraint(fields=['child', 'main', 'launch', 'user'], condition=Q(parent=None), name='Tmp_operation_value_unique_constraint_0'),
            UniqueConstraint(fields=['child', 'main', 'launch', 'parent', 'user'], name='Tmp_operation_value_unique_constraint_1'),
        ]
