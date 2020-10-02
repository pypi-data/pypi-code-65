import logging

from django.db import transaction
from django.db.models import PositiveIntegerField, CheckConstraint, Q, F
from django.forms import model_to_dict

from isc_common import setAttr, delAttr
from isc_common.bit import TurnBitOn
from isc_common.common import uuid4
from isc_common.common.functions import delete_dbl_spaces
from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditQuerySet
from isc_common.models.tree_audit import TreeAuditModelManager
from isc_common.number import StrToNumber
from isc_common.progress import managed_progress, ProgressDroped
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.item_refs import Item_refs
from kaf_pas.kd.models.document_attributes import Document_attributes, Document_attributesManager

logger = logging.getLogger(__name__)


class Item_lineQuerySet(AuditQuerySet):

    def _check(self, **kwargs):
        if kwargs.get('parent') is not None:
            if kwargs.get('parent' == kwargs.get('child')):
                raise Exception('Attempt to write circular reference')

    def _checkDefaults(self, defaults):
        if defaults is not None:
            if (defaults.get("SPC_CLM_MARK_id") is None and defaults.get("SPC_CLM_NAME_id") is None) and (defaults.get("SPC_CLM_MARK") is None and defaults.get("SPC_CLM_NAME") is None):
                raise Exception(f'SPC_CLM_MARK and SPC_CLM_NAME not been Null together. ({defaults})')

    def create(self, **kwargs):
        self._check(**kwargs)
        section = kwargs.get('section')
        section_num = Item_lineManager.section_num(section)
        setAttr(kwargs, 'section_num', section_num)
        return super().create(**kwargs)

    def get_or_create(self, defaults=None, **kwargs):
        self._check(**kwargs)
        self._checkDefaults(defaults)
        section = kwargs.get('section')
        if section:
            section_num = Item_lineManager.section_num(section)
            setAttr(kwargs, 'section_num', section_num)
        elif isinstance(defaults, dict):
            section = defaults.get('section')
            section_num = Item_lineManager.section_num(section)
            setAttr(defaults, 'section_num', section_num)

        return super().get_or_create(defaults, **kwargs)

    def update(self, **kwargs):
        self._check(**kwargs)
        section = kwargs.get('section')
        section_num = Item_lineManager.section_num(section)
        setAttr(kwargs, 'section_num', section_num)
        delAttr(kwargs, 'confirmed')
        delAttr(kwargs, 'edizm__name')
        return super().update(**kwargs)

    def update_or_create(self, defaults=None, **kwargs):
        self._check(**kwargs)
        section = kwargs.get('section')
        self._checkDefaults(defaults)
        if section:
            section_num = Item_lineManager.section_num(section)
            setAttr(kwargs, 'section_num', section_num)
        elif isinstance(defaults, dict):
            section = defaults.get('section')
            section_num = Item_lineManager.section_num(section)
            setAttr(defaults, 'section_num', section_num)
        return super().get_or_create(defaults, **kwargs)


class Item_lineManager(TreeAuditModelManager):
    def get_queryset(self):
        return Item_lineQuerySet(self.model, using=self._db)

    @staticmethod
    def section_num(section):
        sorted_section = {"Документация": 0, "Комплексы": 1, "Сборочные единицы": 2, "Детали": 3, "Стандартные изделия": 4, "Прочие изделия": 5, "Материалы": 6, "Комплекты": 7}
        return sorted_section.get(section)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'child_id': record.child.id if record.child else None,
            'parent_id': record.parent.id,
            'SPC_CLM_FORMAT_id': record.SPC_CLM_FORMAT.id if record.SPC_CLM_FORMAT else None,
            'SPC_CLM_FORMAT__value_str': record.SPC_CLM_FORMAT.value_str if record.SPC_CLM_FORMAT else None,
            'SPC_CLM_ZONE_id': record.SPC_CLM_ZONE.id if record.SPC_CLM_ZONE else None,
            'SPC_CLM_ZONE__value_str': record.SPC_CLM_ZONE.value_str if record.SPC_CLM_ZONE else None,
            'SPC_CLM_POS_id': record.SPC_CLM_POS.id if record.SPC_CLM_POS else None,
            'SPC_CLM_POS__value_str': record.SPC_CLM_POS.value_str if record.SPC_CLM_POS else None,
            'SPC_CLM_POS__value_int': record.SPC_CLM_POS.value_int if record.SPC_CLM_POS else None,
            'SPC_CLM_MARK_id': record.SPC_CLM_MARK.id if record.SPC_CLM_MARK else None,
            'SPC_CLM_MARK__value_str': record.SPC_CLM_MARK.value_str if record.SPC_CLM_MARK else None,
            'SPC_CLM_NAME_id': record.SPC_CLM_NAME.id if record.SPC_CLM_NAME else None,
            'SPC_CLM_NAME__value_str': record.SPC_CLM_NAME.value_str if record.SPC_CLM_NAME else None,
            'SPC_CLM_COUNT_id': record.SPC_CLM_COUNT.id if record.SPC_CLM_COUNT else None,
            'SPC_CLM_COUNT__value_str': record.SPC_CLM_COUNT.value_str if record.SPC_CLM_COUNT else None,
            'SPC_CLM_NOTE_id': record.SPC_CLM_NOTE.id if record.SPC_CLM_NOTE else None,
            'SPC_CLM_NOTE__value_str': record.SPC_CLM_NOTE.value_str if record.SPC_CLM_NOTE else None,
            'SPC_CLM_MASSA_id': record.SPC_CLM_MASSA.id if record.SPC_CLM_MASSA else None,
            'SPC_CLM_MASSA__value_str': record.SPC_CLM_MASSA.value_str if record.SPC_CLM_MASSA else None,
            'SPC_CLM_MATERIAL_id': record.SPC_CLM_MATERIAL.id if record.SPC_CLM_MATERIAL else None,
            'SPC_CLM_MATERIAL__value_str': record.SPC_CLM_MATERIAL.value_str if record.SPC_CLM_MATERIAL else None,
            'SPC_CLM_USER_id': record.SPC_CLM_USER.id if record.SPC_CLM_USER else None,
            'SPC_CLM_USER__value_str': record.SPC_CLM_USER.value_str if record.SPC_CLM_USER else None,
            'SPC_CLM_KOD_id': record.SPC_CLM_KOD.id if record.SPC_CLM_KOD else None,
            'SPC_CLM_KOD__value_str': record.SPC_CLM_KOD.value_str if record.SPC_CLM_KOD else None,
            'SPC_CLM_FACTORY_id': record.SPC_CLM_FACTORY.id if record.SPC_CLM_FACTORY else None,
            'SPC_CLM_FACTORY__value_str': record.SPC_CLM_FACTORY.value_str if record.SPC_CLM_FACTORY else None,
            'edizm_id': record.edizm.id if record.edizm else None,
            'edizm__name': record.edizm.name if record.edizm else None,
            'section': record.section,
            'section_num': record.section_num,
            'subsection': record.subsection,
            'lastmodified': record.lastmodified,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    @staticmethod
    def getIcon(record):
        if record.isFolder:
            return 'folder_256.png'
        elif record.section is not None:
            _section = record.section.lower()
            if _section == 'документация':
                return 'documentation.png'
            elif _section == 'комплексы':
                return 'complexes.png'
            elif _section == 'сборочные единицы':
                return 'assembly.png'
            elif _section == 'детали':
                return 'part.png'
            elif _section == 'стандартные изделия':
                return 'standard_prod.png'
            elif _section == 'прочие изделия':
                return 'other.png'
            elif _section == 'материалы':
                return 'materials.png'
            elif _section == 'комплекты':
                return 'kits.png'
            elif _section == 'ведомость':
                return 'templates.png'
            else:
                return 'question.png'
        else:
            return 'question.png'

    @property
    def item_name(self):
        if self.SPC_CLM_NAME is not None and self.SPC_CLM_MARK is not None:
            return f'{self.SPC_CLM_NAME.value_str}: {self.SPC_CLM_MARK.value_str}'
        elif self.SPC_CLM_NAME is None and self.SPC_CLM_MARK is not None:
            return self.SPC_CLM_MARK.value_str
        elif self.SPC_CLM_NAME is not None and self.SPC_CLM_MARK is None:
            return self.SPC_CLM_NAME.value_str
        else:
            return 'Неизвестен'

    def createFromRequest(self, request, removed=None, function=None):
        request = DSRequest(request=request)
        data = request.get_data()

        parent_id = data.get('parent_id')
        child_id = data.get('child_id')

        if parent_id is None:
            raise Exception('parent_id is None')

        if child_id is None:
            raise Exception('child_id is None')

        with transaction.atomic():

            _data = dict(
                parent_id=parent_id,
                child_id=child_id,

                SPC_CLM_FORMAT_id=data.get('SPC_CLM_FORMAT_id'),
                SPC_CLM_ZONE_id=data.get('SPC_CLM_ZONE_id'),
                SPC_CLM_POS_id=data.get('SPC_CLM_POS_id'),
                SPC_CLM_MARK_id=data.get('SPC_CLM_MARK_id'),
                SPC_CLM_NAME_id=data.get('SPC_CLM_NAME_id'),
                SPC_CLM_COUNT_id=data.get('SPC_CLM_COUNT_id'),
                SPC_CLM_NOTE_id=data.get('SPC_CLM_NOTE_id'),
                SPC_CLM_MASSA_id=data.get('SPC_CLM_MASSA_id'),
                SPC_CLM_MATERIAL_id=data.get('SPC_CLM_MATERIAL_id'),
                SPC_CLM_USER_id=data.get('SPC_CLM_USER_id'),
                SPC_CLM_KOD_id=data.get('SPC_CLM_KOD_id'),
                SPC_CLM_FACTORY_id=data.get('SPC_CLM_FACTORY_id'),
                section=data.get('section'),
                subsection=data.get('subsection'),
            )

            if data.get('SPC_CLM_MARK_id') is None and data.get('SPC_CLM_NAME_id') is None:
                raise Exception(f'SPC_CLM_MARK and SPC_CLM_NAME not been Null together. ({self.model})')

            Item_refs.objects.get_or_create(child_id=child_id, parent_id=parent_id)

            res = super().create(**_data)
            setAttr(data, 'id', res.id)
        return data

    def updateFromRequest(self, request, removed=None, function=None):
        request = DSRequest(request=request)
        data = request.get_data()
        data_res = request.get_data()
        mode = data.get('mode')

        if mode == 'item_spw_replace':
            dropRecords = data.get('dropRecords')

            if not dropRecords:
                raise Exception('Не выбран источник замены.')

            targetRecord = data.get('targetRecord')

            if not targetRecord:
                raise Exception('Не выбрана цель замены.')

            dropRecord = dropRecords[0]

            with transaction.atomic():
                targetLine = Item_line.objects.get(child_id=targetRecord.get('child_id'), parent_id=targetRecord.get('parent_id'))
                dropItem = Item.objects.get(id=dropRecord.get('id'))

                try:
                    Item_refs.objects.get(child=targetLine.child, parent_id=targetLine.parent).delete()
                except Item_refs.DoesNotExist:
                    pass

                targetLine.child_id = dropItem.id
                targetLine.SPC_CLM_NAME = dropItem.STMP_1
                setAttr(targetRecord, 'child_id', dropItem.id)
                setAttr(targetRecord, 'SPC_CLM_NAME_id', dropItem.STMP_1.id if dropItem.STMP_1 else None)
                setAttr(targetRecord, 'SPC_CLM_NAME__value_str', dropItem.STMP_1.value_str if dropItem.STMP_1 else None)
                setAttr(targetRecord, 'SPC_CLM_MARK_id', dropItem.STMP_2.id if dropItem.STMP_2 else None)
                setAttr(targetRecord, 'SPC_CLM_MARK__value_str', dropItem.STMP_2.value_str if dropItem.STMP_2 else None)
                targetLine.SPC_CLM_MARK = dropItem.STMP_2
                targetLine.save()

                Item_refs.objects.get_or_create(child=targetLine.child, parent=targetLine.parent)
                setAttr(targetRecord, 'confirmed', dropRecord.get('confirmed'))
                setAttr(targetRecord, 'relevant', dropRecord.get('relevant'))

                return targetRecord

        relevant = data.get('relevant')
        confirmed = data.get('confirmed')
        item_props = data.get('item_props')
        child_id = data.get('child_id')
        section = data.get('section')

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

        delAttr(data, 'document_id')
        delAttr(data, 'isFolder')
        delAttr(data, 'icon')
        delAttr(data, 'groupParentId')
        delAttr(data, 'where_from')
        delAttr(data, 'relevant')
        delAttr(data, 'confirmed')
        delAttr(data, 'line_id')
        delAttr(data, 'item_props')
        delAttr(data, 'mode')
        _data = dict()

        params = dict()
        for key, val in data.items():
            if str(key).find('SPC_CLM_') != -1:
                if str(key).find('_id') != -1:
                    if val is not None:
                        setAttr(params, key, val)
                elif str(key).find('__value_str') != -1:
                    if val is not None:
                        setAttr(params, key, val)
                elif str(key).find('__value_int') != -1:
                    if val is not None:
                        setAttr(params, key, val)
            else:
                setAttr(_data, key, val)

        with transaction.atomic():
            res_params=dict()
            for key, val in params.items():
                idx = str(key).find('_id')
                if idx != -1:
                    _key = str(key)[0:idx]
                    param_str = params.get(f'{_key}__value_str')
                    param_int = params.get(f'{_key}__value_int')

                    if param_int is not None:
                        if StrToNumber(param_str) != param_int:
                            param_str = str(param_int)

                    attr, _ = Document_attributesManager.get_or_create_attribute(_key, param_str)
                    setAttr(res_params, _key, attr)
                    setAttr(res_params, 'section', section)

            Item.objects.update_or_create(id=child_id, defaults=dict(props=item_props))
            delAttr(_data, 'edizm__name')
            delAttr(_data, 'section')
            delAttr(_data, 'section_num')
            delAttr(_data, 'subsection')
            delAttr(_data, 'lastmodified')
            delAttr(_data, 'editing')
            delAttr(_data, 'deliting')
            delAttr(_data, 'id')
            delAttr(_data, 'parent_id')
            delAttr(_data, 'child_id')

            child = Item.objects.get(id=data.get('child_id'))
            parent = Item.objects.get(id=data.get('parent_id'))

            res_params.update(_data)
            updated = Item_line.objects.filter(child=child, parent=parent).update(**res_params)
            logger.debug(f'updated: {updated}')
        return data_res

    def copyFromRequest(self, request, removed=None, ):
        from kaf_pas.ckk.models.item_line_view import Item_line_view

        request = DSRequest(request=request)

        data = request.json.get('data')
        res = None
        with managed_progress(
                qty=len(data.get('records')),
                id=uuid4(),
                user=request.user,
                title="Выполнено",
                props=TurnBitOn(0, 0)
        ) as progress:
            with transaction.atomic():
                progress.setContentsLabel('<b>Создание строк детализации</b>')
                for record in data.get('records'):
                    if record.get("parent_id") is None:
                        raise Exception('Верхний уровень не подлежит внесению в детализацию.')

                    query = Item_line_view.objects.filter(
                        SPC_CLM_NAME_id=record.get('STMP_1_id'),
                        SPC_CLM_MARK_id=record.get('STMP_2_id')
                    )

                    if query.count() == 0:
                        query = Item_line_view.objects.filter(
                            SPC_CLM_NAME__value_str__delete_dbl_spaces=delete_dbl_spaces(record.get('STMP_1__value_str')),
                            SPC_CLM_MARK__value_str__delete_dbl_spaces=delete_dbl_spaces(record.get('STMP_2__value_str'))
                        )

                    if query.count() > 0:
                        item_line = query[0]
                        res, _ = Item_line.objects.get_or_create(
                            parent_id=record.get("parent_id"),
                            child_id=record.get("id"),
                            SPC_CLM_FORMAT=item_line.SPC_CLM_FORMAT,
                            SPC_CLM_ZONE=item_line.SPC_CLM_ZONE,
                            SPC_CLM_POS=item_line.SPC_CLM_POS,
                            SPC_CLM_MARK=item_line.SPC_CLM_MARK,
                            SPC_CLM_NAME=item_line.SPC_CLM_NAME,
                            SPC_CLM_COUNT=item_line.SPC_CLM_COUNT,
                            SPC_CLM_NOTE=item_line.SPC_CLM_NOTE,
                            SPC_CLM_MASSA=item_line.SPC_CLM_MASSA,
                            SPC_CLM_MATERIAL=item_line.SPC_CLM_MATERIAL,
                            SPC_CLM_USER=item_line.SPC_CLM_USER,
                            SPC_CLM_KOD=item_line.SPC_CLM_USER,
                            SPC_CLM_FACTORY=item_line.SPC_CLM_FACTORY,
                            section=item_line.section,
                            section_num=item_line.section_num,
                            subsection=item_line.subsection,
                        )
                    else:
                        res = Item_line.objects.create(
                            parent_id=record.get("parent_id"),
                            child_id=record.get("id"),
                            SPC_CLM_NAME_id=record.get('STMP_1_id'),
                            SPC_CLM_MARK_id=record.get('STMP_2_id'),
                            SPC_CLM_COUNT=Document_attributesManager.get_or_create_attribute('SPC_CLM_COUNT', '1')[0],
                            section='Сборочные единицы',
                        )

                    if progress.step() != 0:
                        raise ProgressDroped()
            return model_to_dict(res)

    def lookupFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()

        attr_type__code = data.get('attr_type__code')
        value_str = data.get(f'{attr_type__code}__value_str')
        value_int = data.get(f'{attr_type__code}__value_int')

        if value_str is None and value_int is not None:
            value_str = str(value_int)

        if value_str is None:
            return None

        res, created = Document_attributesManager.get_or_create_attribute(attr_codes=attr_type__code, value_str=value_str)
        res = model_to_dict(res)
        if res.get('value_str') == 'null':
            setAttr(res, 'value_str', None)
        return res

    def deleteFromRequest(self, request, removed=None, ):
        from kaf_pas.ckk.models.item_refs import Item_refs
        request = DSRequest(request=request)
        res = 0
        with transaction.atomic():
            for id, mode in request.get_tuple_ids():
                if mode == 'hide':
                    pass
                elif mode == 'visible':
                    pass
                else:
                    for item_line in super().filter(id=id).select_for_update():
                        Item_refs.objects1.filter(parent=item_line.parent, child=item_line.child).delete_with_checked()
                        item_line.delete()
                        res += 1
        return res


class Item_line(AuditModel):
    parent = ForeignKeyProtect(Item, verbose_name='Товарная позиция', related_name='item_parent')
    child = ForeignKeyProtect(Item, verbose_name='Товарная позиция', related_name='item_child')

    SPC_CLM_FORMAT = ForeignKeyProtect(Document_attributes, verbose_name='Формат', related_name='Item_line_SPC_CLM_FORMAT', null=True, blank=True)
    SPC_CLM_ZONE = ForeignKeyProtect(Document_attributes, verbose_name='Зона', related_name='Item_line_SPC_CLM_ZONE', null=True, blank=True)
    SPC_CLM_POS = ForeignKeyProtect(Document_attributes, verbose_name='Позиция', related_name='Item_line_SPC_CLM_POS', null=True, blank=True)
    SPC_CLM_MARK = ForeignKeyProtect(Document_attributes, verbose_name='Обозначение', related_name='Item_line_SPC_CLM_MARK', null=True, blank=True)
    SPC_CLM_NAME = ForeignKeyProtect(Document_attributes, verbose_name='Наименование', related_name='Item_line_SPC_CLM_NAME', null=True, blank=True)
    SPC_CLM_COUNT = ForeignKeyProtect(Document_attributes, verbose_name='Количество', related_name='Item_line_SPC_CLM_COUNT', null=True, blank=True)
    SPC_CLM_NOTE = ForeignKeyProtect(Document_attributes, verbose_name='Примечание', related_name='Item_line_SPC_CLM_NOTE', null=True, blank=True)
    SPC_CLM_MASSA = ForeignKeyProtect(Document_attributes, verbose_name='Масса', related_name='Item_line_SPC_CLM_MASSA', null=True, blank=True)
    SPC_CLM_MATERIAL = ForeignKeyProtect(Document_attributes, verbose_name='Материал', related_name='Item_line_SPC_CLM_MATERIAL', null=True, blank=True)
    SPC_CLM_USER = ForeignKeyProtect(Document_attributes, verbose_name='Пользовательская', related_name='Item_line_SPC_CLM_USER', null=True, blank=True)
    SPC_CLM_KOD = ForeignKeyProtect(Document_attributes, verbose_name='Код', related_name='Item_line_SPC_CLM_KOD', null=True, blank=True)
    SPC_CLM_FACTORY = ForeignKeyProtect(Document_attributes, verbose_name='Предприятие - изготовитель', related_name='Item_line_SPC_CLM_FACTORY', null=True, blank=True)
    edizm = ForeignKeyProtect(Ed_izm, verbose_name='Единица измерения', related_name='Item_line_EdIzm', null=True, blank=True)
    section = CodeField()
    section_num = PositiveIntegerField(null=True, blank=True)
    subsection = NameField()

    Документ_на_материал = ForeignKeyProtect(Document_attributes, related_name='Документ_на_материал_Item_line', null=True, blank=True)
    Наименование_материала = ForeignKeyProtect(Document_attributes, related_name='Наименование_материала_Item_line', null=True, blank=True)
    Документ_на_сортамент = ForeignKeyProtect(Document_attributes, related_name='Документ_на_сортамент_Item_line', null=True, blank=True)
    Наименование_сортамента = ForeignKeyProtect(Document_attributes, related_name='Наименование_сортамента_Item_line', null=True, blank=True)

    objects = Item_lineManager()

    @property
    def qty(self):
        if self.SPC_CLM_COUNT is None:
            return None

        if self.SPC_CLM_COUNT.value_int is None:
            return StrToNumber(self.SPC_CLM_COUNT.value_str)
        return self.SPC_CLM_COUNT.value_int

    def __str__(self):
        return f'\nparent: [{self.parent}]\n' \
               f'\nchild: [{self.child}]\n' \
               f'\nSPC_CLM_FORMAT: [{self.SPC_CLM_FORMAT}]' \
               f'\nSPC_CLM_ZONE: [{self.SPC_CLM_ZONE}]' \
               f'\nSPC_CLM_POS: [{self.SPC_CLM_POS}]' \
               f'\nSPC_CLM_MARK: [{self.SPC_CLM_MARK}]' \
               f'\nSPC_CLM_NAME: [{self.SPC_CLM_NAME}]' \
               f'\nSPC_CLM_COUNT: [{self.SPC_CLM_COUNT}]' \
               f'\nSPC_CLM_NOTE: [{self.SPC_CLM_NOTE}]' \
               f'\nSPC_CLM_MASSA: [{self.SPC_CLM_MASSA}]' \
               f'\nSPC_CLM_MATERIAL: [{self.SPC_CLM_MATERIAL}]' \
               f'\nSPC_CLM_USER: [{self.SPC_CLM_USER}]' \
               f'\nSPC_CLM_KOD: [{self.SPC_CLM_KOD}' \
               f'\nSPC_CLM_FACTORY: [{self.SPC_CLM_FACTORY}]\n' \
               f'\nEdIzm: [{self.edizm}]\n' \
               f'section: {self.section}\n' \
               f'subsection: {self.subsection}\n\n'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Строка состава изделия'
        unique_together = (('parent', 'child'),)
        constraints = [CheckConstraint(check=~Q(child=F('parent')), name='Item_line_not_circulate_refs')]
        ordering = ['section']
