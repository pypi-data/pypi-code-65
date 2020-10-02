import logging

from bitfield import BitField

from isc_common.bit import IsBitOn
from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.name_field import NameStrictField
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.base_ref import BaseRefHierarcy, BaseRefQuerySet
from isc_common.number import DelProps

logger = logging.getLogger(__name__)


class OperationsQuerySet(BaseRefQuerySet, CommonManagetWithLookUpFieldsQuerySet):
    pass


class OperationsManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            'absorption': record.props.absorption,
            'code': record.code,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'full_name': record.full_name,
            'id': record.id,
            'lastmodified': record.lastmodified,
            'launched': record.props.launched,
            'name': record.name,
            'parent_id': record.parent_id,
            # 'partition_to_launch': record.props.partition_to_launch,
            'props': record.props,
            'transportation': record.props.transportation,
        }
        return DelProps(res)

    def get_queryset(self):
        return OperationsQuerySet(self.model, using=self._db)

    @staticmethod
    def get_props():
        return BitField(flags=(
            ('launched', 'Возможность привязки к запуску'),  # 0
            ('grouped', 'Группировка'),  # 1
            ('transportation', 'Операция транспортировки'),  # 2
            ('absorption', 'Операция поглощения'),  # 3
        ), default=0, db_index=True)


class Operations(BaseRefHierarcy):
    code = CodeStrictField(unique=True)
    name = NameStrictField()
    props = OperationsManager.get_props()

    @property
    def attrs(self):
        from kaf_pas.production.models.operation_attr import Operation_attr
        return [item.attr_type.code for item in Operation_attr.objects.filter(operation=self)]

    @property
    def is_launched(self):
        return IsBitOn(self.props, Operations.props.launched)
        # return True

    @property
    def is_grouped(self):
        return IsBitOn(self.props, Operations.props.grouped)

    @property
    def is_transportation(self):
        return IsBitOn(self.props, Operations.props.transportation)

    @property
    def is_absorption(self):
        return IsBitOn(self.props, Operations.props.absorption)

    objects = OperationsManager()

    def __str__(self):
        return f'ID={self.id}, code={self.code}, name={self.name} , props={self.props} , description={self.description}'

    class Meta:
        verbose_name = 'Операции'
        db_constraints = {
            'Operations_not_cycled': 'CHECK ("id" != "parent_id")',
        }
