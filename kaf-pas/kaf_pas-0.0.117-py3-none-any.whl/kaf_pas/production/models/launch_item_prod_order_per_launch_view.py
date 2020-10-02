import logging

from django.db.models import PositiveIntegerField, BooleanField, DecimalField

from isc_common.common import blinkString
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade, ForeignKeySetNull
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from isc_common.models.standard_colors import Standard_colors
from isc_common.number import DelProps, DecimalToStr
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.item import Item_add, Item
from kaf_pas.ckk.models.item_line import Item_line, Item_lineManager
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.production.models.launches import Launches

logger = logging.getLogger(__name__)


class launch_item_prod_order_per_launch_viewQuerySet(AuditQuerySet):
    pass


class launch_item_prod_order_per_launch_viewManager(AuditManager):

    @staticmethod
    def get_buffer_oddment_value(value):
        if value is None:
            return None
        return blinkString(text=DecimalToStr(value), blink=True if value < 0 else False, bold=True, color='green' if value > 0 else 'red')

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
            'parent_id': record.parent.id,
            'qty_doc': DecimalToStr(record.qty_doc),
            'qty_exists': launch_item_prod_order_per_launch_viewManager.get_buffer_oddment_value(record.qty_exists),
            'qty_per_one': DecimalToStr(record.qty_per_one) if record.section != 'Документация' else None,
            'relevant': record.relevant,
            'section': record.section,
            'section_num': Item_lineManager.section_num(record.section),
            'SPC_CLM_MARK__value_str': record.SPC_CLM_MARK.value_str if record.SPC_CLM_MARK else None,
            'SPC_CLM_MARK_id': record.SPC_CLM_MARK.id if record.SPC_CLM_MARK else None,
            'SPC_CLM_NAME__value_str': record.SPC_CLM_NAME.value_str if record.SPC_CLM_NAME else None,
            'SPC_CLM_NAME_id': record.SPC_CLM_NAME.id if record.SPC_CLM_NAME else None,
            'subsection': record.subsection,
            'where_from': record.where_from,
            'color_id': record.color.id if record.color and record.color else None,
            'color__name': record.color.name if record.color and record.color else None,
            'color__color': record.color.color if record.color and record.color else None,
        }
        return DelProps(res)

    def get_queryset(self):
        return launch_item_prod_order_per_launch_viewQuerySet(self.model, using=self._db)


class Launch_item_prod_order_per_launch_view(AuditModel):
    parent = ForeignKeyProtect(Item, verbose_name='Товарная позиция', related_name='item_parent_p_launch')
    child = ForeignKeyCascade(Item, verbose_name='Товарная позиция', related_name='item_child_p_launch')

    SPC_CLM_MARK = ForeignKeyProtect(Document_attributes, verbose_name='Обозначение', related_name='SPC_CLM_MARK_p_launch', null=True, blank=True)
    SPC_CLM_NAME = ForeignKeyProtect(Document_attributes, verbose_name='Наименование', related_name='SPC_CLM_NAME_p_launch', null=True, blank=True)

    item = ForeignKeyProtect(Item, related_name='Item_p')
    edizm = ForeignKeyProtect(Ed_izm, verbose_name='Единица измерения', related_name='EdIzm_p_launch', null=True, blank=True)
    section = NameField()
    section_num = PositiveIntegerField(default=0)
    subsection = NameField()
    item_line = ForeignKeySetNull(Item_line, null=True, blank=True)
    color = ForeignKeyProtect(Standard_colors, null=True, blank=True, related_name='launch_item_prod_order_per_launch_view_color')
    colorb = ForeignKeyProtect(Standard_colors, null=True, blank=True, related_name='launch_item_prod_order_per_launch_view_colorb')
    launch = ForeignKeyProtect(Launches, related_name='launch_item_prod_order_per_launch_view_colorb')

    qty_doc = DecimalField(decimal_places=4, max_digits=19)
    qty_per_one = DecimalField(decimal_places=4, max_digits=19)
    qty_exists = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    qty_odd = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)

    where_from = NameField()
    item_props = Item_add.get_prop_field()
    relevant = NameField()
    enabled = BooleanField()

    objects = launch_item_prod_order_per_launch_viewManager()

    def __str__(self):
        return f'child: [{self.child}], qty_exists: {self.qty_exists}'

    class Meta:
        verbose_name = 'Строка состава изделия в производственной спецификации'
        db_table = 'production_launch_item_prod_order_per_launch_view'
        managed = False
        # proxy = True
