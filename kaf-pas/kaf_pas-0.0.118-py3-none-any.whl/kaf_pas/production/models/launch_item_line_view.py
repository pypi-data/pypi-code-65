import logging

from django.contrib.postgres.fields import ArrayField
from django.db import transaction
from django.db.models import PositiveIntegerField, BooleanField, DecimalField, BigIntegerField

from isc_common import delAttr, setAttr
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade, ForeignKeySetNull
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from isc_common.models.standard_colors import Standard_colors
from isc_common.number import DelProps, DecimalToStr
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.item import Item_add, Item
from kaf_pas.ckk.models.item_line import Item_line
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.production.models.launch_item_view import Launch_item_viewManager
from kaf_pas.production.models.launches import Launches

logger = logging.getLogger(__name__)


class Launch_item_line_viewQuerySet(AuditQuerySet):
    def get_range_rows1(self, request, function=None, distinct_field_names=None, remove_fields=None):
        request = DSRequest(request=request)

        # Необходимо в производственной спецификации
        data = request.get_data()
        delAttr(data, 'launch_id')
        # launch_id = data.get('launch_id')
        # if launch_id is not None:
        #     launch = Launches.objects.get(id=launch_id)
        #     child_launches = launch.child_launches
        #     setAttr(data, 'launch_id', list(map(lambda x: x.id, child_launches)) if len(child_launches) > 0 else [launch.id])

        request.set_data(data)

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

    def get_range_rows2(self, request, function=None):
        request = DSRequest(request=request)
        data = request.get_data()
        # launch_id = data.get('launch_id')
        # launch_id = [launch.id for launch in Launches.objects.filter(parent_id=launch_id)]
        # setAttr(data, 'launch_id', launch_id)
        delAttr(data, 'launch_id')
        request.set_data(data)

        self.alive_only = request.alive_only
        self.enabledAll = request.enabledAll
        res = self.get_range_rows(
            start=request.startRow,
            end=request.endRow,
            function=function,
            json=request.json,
            criteria=request.get_criteria(),
            user=request.user
        )
        return res

    def get_info(self, request, *args):
        request = DSRequest(request=request)
        data = request.get_data()
        delAttr(data, 'launch_id')
        request.set_data(data)
        criteria = self.get_criteria(json=request.json)
        cnt = super().filter(*args, criteria).count()
        cnt_all = super().filter().count()
        return dict(qty_rows=cnt, all_rows=cnt_all)


class Launch_item_line_viewManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'child_id': record.child.id,
            'deliting': record.deliting,
            'editing': record.editing,
            'edizm__name': record.edizm.name if record.edizm else None,
            'edizm_id': record.edizm.id if record.edizm else None,
            'enabled': record.enabled,
            'id': record.id,
            'item_props': record.item_props,
            'lastmodified': record.lastmodified,
            # 'launch_id': record.launch.id,
            'parent_id': record.parent.id,
            'qty_doc': DecimalToStr(record.qty_doc),
            'qty_per_one': DecimalToStr(record.qty_per_one) if record.section != 'Документация' else None,
            'relevant': record.relevant,
            'section': record.section,
            'section_num': record.section_num,
            'SPC_CLM_FACTORY__value_str': record.SPC_CLM_FACTORY.value_str if record.SPC_CLM_FACTORY else None,
            'SPC_CLM_FACTORY_id': record.SPC_CLM_FACTORY.id if record.SPC_CLM_FACTORY else None,
            'SPC_CLM_FORMAT__value_str': record.SPC_CLM_FORMAT.value_str if record.SPC_CLM_FORMAT else None,
            'SPC_CLM_FORMAT_id': record.SPC_CLM_FORMAT.id if record.SPC_CLM_FORMAT else None,
            'SPC_CLM_KOD__value_str': record.SPC_CLM_KOD.value_str if record.SPC_CLM_KOD else None,
            'SPC_CLM_KOD_id': record.SPC_CLM_KOD.id if record.SPC_CLM_KOD else None,
            'SPC_CLM_MARK__value_str': record.SPC_CLM_MARK.value_str if record.SPC_CLM_MARK else None,
            'SPC_CLM_MARK_id': record.SPC_CLM_MARK.id if record.SPC_CLM_MARK else None,
            'SPC_CLM_MASSA__value_str': record.SPC_CLM_MASSA.value_str if record.SPC_CLM_MASSA else None,
            'SPC_CLM_MASSA_id': record.SPC_CLM_MASSA.id if record.SPC_CLM_MASSA else None,
            'SPC_CLM_MATERIAL__value_str': record.SPC_CLM_MATERIAL.value_str if record.SPC_CLM_MATERIAL else None,
            'SPC_CLM_MATERIAL_id': record.SPC_CLM_MATERIAL.id if record.SPC_CLM_MATERIAL else None,
            'SPC_CLM_NAME__value_str': record.SPC_CLM_NAME.value_str if record.SPC_CLM_NAME else None,
            'SPC_CLM_NAME_id': record.SPC_CLM_NAME.id if record.SPC_CLM_NAME else None,
            'SPC_CLM_NOTE__value_str': record.SPC_CLM_NOTE.value_str if record.SPC_CLM_NOTE else None,
            'SPC_CLM_NOTE_id': record.SPC_CLM_NOTE.id if record.SPC_CLM_NOTE else None,
            'SPC_CLM_POS__value_int': record.SPC_CLM_POS.value_int if record.SPC_CLM_POS else None,
            'SPC_CLM_POS__value_str': record.SPC_CLM_POS.value_str if record.SPC_CLM_POS else None,
            'SPC_CLM_POS_id': record.SPC_CLM_POS.id if record.SPC_CLM_POS else None,
            'SPC_CLM_USER__value_str': record.SPC_CLM_USER.value_str if record.SPC_CLM_USER else None,
            'SPC_CLM_USER_id': record.SPC_CLM_USER.id if record.SPC_CLM_USER else None,
            'SPC_CLM_ZONE__value_str': record.SPC_CLM_ZONE.value_str if record.SPC_CLM_ZONE else None,
            'SPC_CLM_ZONE_id': record.SPC_CLM_ZONE.id if record.SPC_CLM_ZONE else None,
            'subsection': record.subsection,
            'where_from': record.where_from,
            'color_id': record.color.id if record.color and record.color else None,
            'color__name': record.color.name if record.color and record.color else None,
            'color__color': record.color.color if record.color and record.color else None,
        }
        return DelProps(res)

    def updateFromRequest(self, request, removed=None, function=None):
        request = DSRequest(request=request)
        id = request.get_id()
        data = request.get_data()
        data_res = data.copy()
        Launch_item_viewManager.check_launch(launch=Launches.objects.get(id=data.get('launch_id')))

        relevant = data.get('relevant')
        confirmed = data.get('confirmed')
        item_props = data.get('item_props')
        child_id = data.get('child_id')

        if relevant == 'Актуален':
            item_props |= Item.props.relevant
            # setAttr(data_res, 'relevant', 'Актуален')

        elif relevant == 'Не актуален':
            item_props &= ~Item.props.relevant
            # setAttr(data_res, 'relevant', 'Не актуален')

        if confirmed == 'Подтвержден':
            item_props |= Item.props.confirmed
            # setAttr(data_res, 'confirmed', 'Подтвержден')

        elif confirmed == 'Не подтвержден':
            item_props &= ~Item.props.confirmed
            # setAttr(data_res, 'confirmed', 'Не подтвержден')

        delAttr(data, 'isFolder')
        delAttr(data, 'icon')
        delAttr(data, 'groupParentId')
        delAttr(data, 'where_from')
        delAttr(data, 'relevant')
        delAttr(data, 'confirmed')
        delAttr(data, 'line_id')
        delAttr(data, 'edizm__name')
        _data = dict()

        for key, val in data.items():
            if str(key).find('__value_str') == -1 and str(key).find('__value_int') == -1:
                setAttr(_data, key, val)

        with transaction.atomic():
            super().filter(id=id).update(**_data)
            Item.objects.update_or_create(id=child_id, defaults=dict(props=item_props))
        return data_res

    def deleteFromRequest(self, request, removed=None, ):
        request = DSRequest(request=request)
        res = 0
        tuple_ids = request.get_tuple_ids()
        with transaction.atomic():
            for id, mode in tuple_ids:
                if mode == 'hide':
                    super().filter(id=id).soft_delete()
                elif mode == 'visible':
                    super().filter(id=id).soft_restore()
                else:
                    Launch_item_viewManager.check_launch(launch=Launch_item_line_view.objects.get(id=id).launch)
                    qty, _ = super().filter(id=id).delete()
                res += qty
        return res

    def get_queryset(self):
        return Launch_item_line_viewQuerySet(self.model, using=self._db)


class Launch_item_line_view(AuditModel):
    parent = ForeignKeyProtect(Item, verbose_name='Товарная позиция', related_name='item_parent_l')
    child = ForeignKeyCascade(Item, verbose_name='Товарная позиция', related_name='item_child_l')

    SPC_CLM_FORMAT = ForeignKeyProtect(Document_attributes, verbose_name='Формат', related_name='SPC_CLM_FORMAT_l', null=True, blank=True)
    SPC_CLM_ZONE = ForeignKeyProtect(Document_attributes, verbose_name='Зона', related_name='SPC_CLM_ZONE_l', null=True, blank=True)
    SPC_CLM_POS = ForeignKeyProtect(Document_attributes, verbose_name='Позиция', related_name='SPC_CLM_POS_l', null=True, blank=True)
    SPC_CLM_MARK = ForeignKeyProtect(Document_attributes, verbose_name='Обозначение', related_name='SPC_CLM_MARK_l', null=True, blank=True)
    SPC_CLM_NAME = ForeignKeyProtect(Document_attributes, verbose_name='Наименование', related_name='SPC_CLM_NAME_l', null=True, blank=True)
    SPC_CLM_NOTE = ForeignKeyProtect(Document_attributes, verbose_name='Примечание', related_name='SPC_CLM_NOTE_l', null=True, blank=True)
    SPC_CLM_MASSA = ForeignKeyProtect(Document_attributes, verbose_name='Масса', related_name='SPC_CLM_MASSA_l', null=True, blank=True)
    SPC_CLM_MATERIAL = ForeignKeyProtect(Document_attributes, verbose_name='Материал', related_name='SPC_CLM_MATERIAL_l', null=True, blank=True)
    SPC_CLM_USER = ForeignKeyProtect(Document_attributes, verbose_name='Пользовательская', related_name='SPC_CLM_USER_l', null=True, blank=True)
    SPC_CLM_KOD = ForeignKeyProtect(Document_attributes, verbose_name='Код', related_name='SPC_CLM_KOD_l', null=True, blank=True)
    SPC_CLM_FACTORY = ForeignKeyProtect(Document_attributes, verbose_name='Предприятие - изготовитель', related_name='SPC_CLM_FACTORY_l', null=True, blank=True)
    edizm = ForeignKeyProtect(Ed_izm, verbose_name='Единица измерения', related_name='EdIzm_l', null=True, blank=True)
    section = NameField()
    section_num = PositiveIntegerField(default=0)
    subsection = NameField()
    item_line = ForeignKeySetNull(Item_line, null=True, blank=True)
    # launch = ForeignKeyProtect(Launches)
    launch_ids = ArrayField(BigIntegerField(), default=list)
    color = ForeignKeyProtect(Standard_colors, null=True, blank=True)

    qty_doc = DecimalField(decimal_places=4, max_digits=19)
    qty_per_one = DecimalField(decimal_places=4, max_digits=19)
    qty_exists = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)

    where_from = NameField()
    item_props = Item_add.get_prop_field()
    relevant = NameField()
    enabled = BooleanField()

    objects = Launch_item_line_viewManager()

    class Meta:
        verbose_name = 'Строка состава изделия в производственной спецификации'
        db_table = 'production_launch_item_line_view'
        managed = False
        # proxy = True
