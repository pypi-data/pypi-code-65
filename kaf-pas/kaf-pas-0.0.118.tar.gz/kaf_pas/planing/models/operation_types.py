import logging

from bitfield import BitField

from isc_common.bit import IsBitOn
from isc_common.models.base_ref import BaseRefManager, BaseRefQuerySet, BaseRefHierarcy
from isc_common.number import DelProps
from kaf_pas.planing.operation_typesStack import ACOUNTING
from kaf_pas.system.models.contants import Contants

logger = logging.getLogger(__name__)


class Operation_typesQuerySet(BaseRefQuerySet):
    def update_or_create(self, defaults=None, **kwargs):
        res = super().update_or_create(**kwargs, defaults=defaults)
        # opt = Operation_types.objects.get(code=kwargs.get('code'))

        _res, _ = res
        if _res.is_accounting:
            logger.debug('Accountiing operations')
            Contants.objects.update_or_create(code=ACOUNTING, value=_res.id, name=f'code: {_res.code}, name: {_res.name}', description=_res.description)
        return res


class Operation_typesManager(BaseRefManager):

    @staticmethod
    def getRecord(record):
        from kaf_pas.planing.models.status_operation_types import Status_operation_typesManager
        from kaf_pas.planing.models.status_operation_types import Status_operation_types
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'full_name': record.full_name,
            'description': record.description,
            'parent_id': record.parent.id if record.parent else None,
            'editing': record.editing,
            'deliting': record.deliting,
            'props': record.props,
            'plus': record.props.plus,
            'minus': record.props.minus,
            'statuses': [Status_operation_typesManager.getRecord(statuses) for statuses in Status_operation_types.objects.filter(opertype_id=record.id)]
        }
        return DelProps(res)

    def get_queryset(self):
        return Operation_typesQuerySet(self.model, using=self._db)


class Operation_types(BaseRefHierarcy):
    props = BitField(flags=(
        ('plus', 'Приходная операция'),  # 0
        ('minus', 'Расходная операция'),  # 1
        ('accounting', 'Операция учета (для подсчета остатков в буферах)'),  # 2
        ('grouping', 'Операция группировки'),  # 3
    ), default=0, db_index=True)

    objects = Operation_typesManager()

    @property
    def is_accounting(self):
        return IsBitOn(self.props, Operation_types.props.accounting)

    @property
    def is_minus(self):
        return IsBitOn(self.props, Operation_types.props.minus)

    @property
    def is_grouping(self):
        return IsBitOn(self.props, Operation_types.props.grouping)

    def __str__(self):
        return f"ID:{self.id}, code: {self.code}, name: {self.name}, full_name: {self.full_name}, parent_id: [{self.parent}], props: {self.props}, description: {self.description}"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Типы системных операций'
