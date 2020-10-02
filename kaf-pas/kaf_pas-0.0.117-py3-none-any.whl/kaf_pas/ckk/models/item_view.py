import logging

from django.conf import settings
from django.core.exceptions import EmptyResultSet
from django.db import transaction
from django.db.models import BigIntegerField, BooleanField, PositiveIntegerField
from django.forms import model_to_dict

from isc_common import delAttr, setAttr
from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.base_ref import Hierarcy
from isc_common.models.tree_audit import TreeAuditModelManager, TreeAuditModelQuerySet
from isc_common.number import DelProps, ToStr
from isc_common.ws.webSocket import WebSocket
from kaf_pas.ckk.models.item import Item_add, Item
from kaf_pas.ckk.models.item_line import Item_lineManager
from kaf_pas.ckk.models.item_refs import Item_refsManager
from kaf_pas.kd.models.document_attributes import Document_attributes
from kaf_pas.kd.models.documents import Documents
from kaf_pas.kd.models.lotsman_documents_hierarcy import Lotsman_documents_hierarcy

logger = logging.getLogger(__name__)


class Item_viewQuerySet(TreeAuditModelQuerySet):
    def get_range_rows_variant(self, request, function=None, distinct_field_names=None, remove_fields=None):
        request = DSRequest(request=request)

        self.alive_only = request.alive_only
        self.enabledAll = request.enabledAll
        data = request.get_data()
        ts = data.get('ts')
        parent_id = data.get('parent_id')
        logger.debug(f'data in : {data}')
        data = dict(ts=ts, parent_id=parent_id)
        logger.debug(f'data out : {data}')
        request.set_data(data)
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

    def get_range_rows(self, start=None, end=None, function=None, json=None, distinct_field_names=None, criteria=None, user=None, *args):
        json = self.rearrange_parent(json=json)

        queryResult = self._get_range_rows(*args, start=start, end=end, function=function, json=json, distinct_field_names=distinct_field_names)
        try:
            logger.debug(f'\n\n{queryResult.query}\n')
        except EmptyResultSet as ex:
            logger.warning(ex)

        if function:
            res = [function(record) for record in queryResult]
        else:
            res = [model_to_dict(record) for record in queryResult]

        return res


class Item_viewManager(TreeAuditModelManager):

    @staticmethod
    def fullRows(suffix=''):
        WebSocket.full_refresh_grid(grid_id=f'{settings.GRID_CONSTANTS.refresh_item_view_grid}{suffix}')

    @staticmethod
    def refreshRows(ids):
        if isinstance(ids, int):
            ids = [ids]
        records = [Item_viewManager.getRecord(record) for record in Item_viewManager.objects.filter(id__in=ids)]
        WebSocket.row_refresh_grid(grid_id=settings.GRID_CONSTANTS.refresh_item_view_grid_row, records=records)

    def updateFromRequest(self, request, removed=None, function=None):
        from kaf_pas.ckk.models.item_refs import Item_refs

        if not isinstance(request, DSRequest):
            request = DSRequest(request=request)
        data = request.get_data()

        with transaction.atomic():

            relevant = data.get('relevant')
            confirmed = data.get('confirmed')

            props = data.get('props', 0)
            refs_props = data.get('refs_props', 0)
            refs_id = data.get('refs_id')

            if relevant == 'Актуален':
                props |= Item.props.relevant
            else:
                props &= ~Item.props.relevant

            if confirmed == 'Подтвержден':
                props |= Item.props.confirmed
            else:
                props &= ~Item.props.confirmed

            where_from = data.get('where_from')
            if where_from == 'Получено из чертежа':
                props |= Item.props.from_cdw
            elif where_from == 'Получено из спецификации':
                props |= Item.props.from_spw
            elif where_from == 'Получено из бумажного архива':
                props |= Item.props.from_pdf
            elif where_from == 'Занесено вручную':
                props |= Item.props.man_input

            delAttr(data, 'relevant')
            delAttr(data, 'confirmed')
            delAttr(data, 'where_from')
            delAttr(data, 'qty_operations')
            delAttr(data, 'refs_props')
            delAttr(data, 'icon')
            setAttr(data, 'props', props)

            Item_refs.objects.filter(id=refs_id).update(props=refs_props)
            res = Item.objects.filter(id=data.get('id')).update(**data)

            return res

    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "STMP_1_id": record.STMP_1.id if record.STMP_1 else None,
            "STMP_1__value_str": ToStr(record.STMP_1.value_str) if record.STMP_1 else None,
            "STMP_2_id": record.STMP_2.id if record.STMP_2 else None,
            "STMP_2__value_str": ToStr(record.STMP_2.value_str) if record.STMP_2 else None,
            "lastmodified": record.lastmodified,
            "document_id": record.document.id if record.document else None,
            "lotsman_document_id": record.lotsman_document.id if record.lotsman_document else None,
            "document__file_document": record.document.file_document if record.document else None,
            "parent_id": record.parent_id,
            "editing": record.editing,
            "deliting": record.deliting,
            "isFolder": record.isFolder,
            "relevant": record.relevant,
            "confirmed": record.confirmed,
            "section": record.section,
            "version": record.version,
            "where_from": record.where_from,
            "isLotsman": record.isLotsman,
            "qty_operations": record.qty_operations,
            "props": record.props,
            "refs_props": record.refs_props,
            'icon': Item_lineManager.getIcon(record)
        }
        # print(res)
        return DelProps(res)

    def get_queryset(self):
        return Item_viewQuerySet(self.model, using=self._db)

    @staticmethod
    def copy_item(item, parent_item, user):
        from kaf_pas.ckk.models.item_refs import Item_refs
        from kaf_pas.ckk.models.item_line import Item_line
        from kaf_pas.ckk.models.item_image_refs import Item_image_refs

        if not isinstance(item, Item_view) and not isinstance(item, Item):
            raise Exception('item must be a Item type')

        key = 'Item_viewManager.copy_item'
        settings.LOCKS.acquire(key)
        dict_item = model_to_dict(item)
        delAttr(dict_item, 'id')
        delAttr(dict_item, 'relevant')
        delAttr(dict_item, 'where_from')
        delAttr(dict_item, 'isFolder')
        setAttr(dict_item, 'user', user)
        setAttr(dict_item, 'STMP_1_id', dict_item.get('STMP_1'))
        setAttr(dict_item, 'STMP_2_id', dict_item.get('STMP_2'))
        setAttr(dict_item, 'document_id', dict_item.get('document'))
        setAttr(dict_item, 'props', Item.props.relevant | Item.props.copied)
        new_item = Item.objects.create(**dict_item)

        Item_refs.objects.get_or_create(parent=parent_item, child=new_item)
        for item_refs in Item_refs.objects.filter(parent_id=item.id):
            Item_refs.objects.get_or_create(parent_id=new_item.id, child=item_refs.child)

        for item_line in Item_line.objects.filter(parent_id=item.id):
            dict_item_line = model_to_dict(item_line)

            delAttr(dict_item_line, 'id')
            setAttr(dict_item_line, 'parent_id', new_item.id)
            delAttr(dict_item_line, 'parent')
            setAttr(dict_item_line, 'child_id', dict_item_line.get('child'))
            delAttr(dict_item_line, 'child')

            setAttr(dict_item_line, 'SPC_CLM_FORMAT_id', dict_item_line.get('SPC_CLM_FORMAT'))
            delAttr(dict_item_line, 'SPC_CLM_FORMAT')
            setAttr(dict_item_line, 'SPC_CLM_ZONE_id', dict_item_line.get('SPC_CLM_ZONE'))
            delAttr(dict_item_line, 'SPC_CLM_ZONE')
            setAttr(dict_item_line, 'SPC_CLM_POS_id', dict_item_line.get('SPC_CLM_POS'))
            delAttr(dict_item_line, 'SPC_CLM_POS')
            setAttr(dict_item_line, 'SPC_CLM_MARK_id', dict_item_line.get('SPC_CLM_MARK'))
            delAttr(dict_item_line, 'SPC_CLM_MARK')
            setAttr(dict_item_line, 'SPC_CLM_NAME_id', dict_item_line.get('SPC_CLM_NAME'))
            delAttr(dict_item_line, 'SPC_CLM_NAME')
            setAttr(dict_item_line, 'SPC_CLM_COUNT_id', dict_item_line.get('SPC_CLM_COUNT'))
            delAttr(dict_item_line, 'SPC_CLM_COUNT')
            setAttr(dict_item_line, 'SPC_CLM_NOTE_id', dict_item_line.get('SPC_CLM_NOTE'))
            delAttr(dict_item_line, 'SPC_CLM_NOTE')
            setAttr(dict_item_line, 'SPC_CLM_MASSA_id', dict_item_line.get('SPC_CLM_MASSA'))
            delAttr(dict_item_line, 'SPC_CLM_MASSA')
            setAttr(dict_item_line, 'SPC_CLM_MATERIAL_id', dict_item_line.get('SPC_CLM_MATERIAL'))
            delAttr(dict_item_line, 'SPC_CLM_MATERIAL')
            setAttr(dict_item_line, 'SPC_CLM_USER_id', dict_item_line.get('SPC_CLM_USER'))
            delAttr(dict_item_line, 'SPC_CLM_USER')
            setAttr(dict_item_line, 'SPC_CLM_KOD_id', dict_item_line.get('SPC_CLM_KOD'))
            delAttr(dict_item_line, 'SPC_CLM_KOD')
            setAttr(dict_item_line, 'SPC_CLM_FACTORY_id', dict_item_line.get('SPC_CLM_FACTORY'))
            delAttr(dict_item_line, 'SPC_CLM_FACTORY')
            Item_line.objects.get_or_create(**dict_item_line)

        for item_image_refs in Item_image_refs.objects.filter(item_id=item.id):
            dict_item_image_refs = model_to_dict(item_image_refs)
            delAttr(dict_item_image_refs, 'id')
            delAttr(dict_item_image_refs, 'item')
            setAttr(dict_item_image_refs, 'item_id', new_item.id)
            setAttr(dict_item_image_refs, 'thumb_id', dict_item_image_refs.get('thumb'))
            delAttr(dict_item_image_refs, 'thumb')
            setAttr(dict_item_image_refs, 'thumb10_id', dict_item_image_refs.get('thumb10'))
            delAttr(dict_item_image_refs, 'thumb10')
            Item_image_refs.objects.get_or_create(**dict_item_image_refs)
        settings.LOCKS.release(key)

        return new_item

    def copyFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()

        with transaction.atomic():
            item = self.get(id=data.get('id'), parent_id=data.get('parent_id'))
            parent_item = Item.objects.get(id=data.get('parent_id'))

            new_item = Item_viewManager.copy_item(item=item, parent_item=parent_item, user=request.user)
            res = model_to_dict(new_item)
            setAttr(res, 'props', res.get('props')._value)

        return res


class Item_view(Hierarcy):
    STMP_1 = ForeignKeyProtect(Document_attributes, verbose_name='Наименование изделия', related_name='STMP_1_view', null=True, blank=True)
    STMP_2 = ForeignKeyProtect(Document_attributes, verbose_name='Обозначение изделия', related_name='STMP_2_view', null=True, blank=True)
    document = ForeignKeyProtect(Documents, verbose_name='Документ', null=True, blank=True)
    lotsman_document = ForeignKeyProtect(Lotsman_documents_hierarcy, verbose_name='Документ из Лоцмана', null=True, blank=True)
    refs_id = BigIntegerField()
    isLotsman = BooleanField()
    relevant = NameField()
    confirmed = NameField()
    where_from = NameField()
    props = Item_add.get_prop_field()
    refs_props = Item_refsManager.props()
    version = PositiveIntegerField(null=True, blank=True)
    section = CodeField(null=True, blank=True)
    qty_operations = PositiveIntegerField()

    isFolder = BooleanField()

    objects = Item_viewManager()

    @property
    def item(self):
        from kaf_pas.ckk.models.item import Item
        return Item.objects.get(id=self.id)

    def __str__(self):
        return f"ID={self.id} STMP_1=[{self.STMP_1}], STMP_2=[{self.STMP_2}], props={self.props}"

    class Meta:
        managed = False
        db_table = 'ckk_item_view'
        verbose_name = 'Товарная позиция'
