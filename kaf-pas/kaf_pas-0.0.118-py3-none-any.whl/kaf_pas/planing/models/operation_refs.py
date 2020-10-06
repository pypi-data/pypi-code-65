import logging

from bitfield import BitField
from django.db.models import CheckConstraint, Q, F, UniqueConstraint

from isc_common import Wrapper, delAttr
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel
from isc_common.models.tree_audit import TreeAuditModelManager, TreeAuditModelQuerySet
from kaf_pas.planing.models.operations import Operations, BaseOperationQuerySet

logger = logging.getLogger(__name__)


class ORF_Wrapper(Wrapper):
    parent = None
    child = None
    parent_id = None
    child_id = None


class Operation_refsQuerySet(TreeAuditModelQuerySet):
    def create(self, **kwargs):
        refs = ORF_Wrapper(**kwargs)

        if not kwargs.get('enable_parent_None'):
            if refs.parent is None and refs.parent_id is None:
                raise Exception('Запись parent is None Запрещена')
        else:
            delAttr(kwargs, 'enable_parent_None')

        return super().create(**kwargs)

    def delete(self):
        self.check_dliting = False

        return super().delete()


class Operation_refsManager(TreeAuditModelManager):

    def delete_m2m(self, operation_refs, props=None):
        if not isinstance(operation_refs, Operation_refs):
            raise Exception(f'element: {operation_refs} must be Operation_refs')

        logger.debug('\noperation_refs: ==================================================')
        logger.debug(f'operation_refs: {operation_refs}')
        logger.debug('operation_refs: ==================================================\n')

        if props is not None:
            query = Operation_refs.objects.filter(child=operation_refs.parent, props=props)
        else:
            query = Operation_refs.objects.filter(child=operation_refs.parent)

        for childs_refs in query:
            logger.debug('\nchilds_refs: ==================================================')
            logger.debug(f'childs_refs: {childs_refs}')
            logger.debug('childs_refs: ==================================================\n')
            childs_refs.child = operation_refs.child
            childs_refs.save()

        deleted = operation_refs.delete()
        logger.debug(f'\ndeleted: {deleted}')

    @staticmethod
    def props():
        return BitField(flags=(
            ('inner_routing', 'Связь операций внутри товарной позиции'),  # 0-1
            ('outer_routing', 'Связь операций между товарными позициями'),  # 1-2
            ('product_order_routing', 'Связи в блоке задания на производство'),  # 2-4
            ('product_making', 'Связи выпуска'),  # 3-8
            ('product_making_block', 'Блок операций выпуска, удаляется как одно целое'),  # 4-16
        ), default=0, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'parent': record.parent.id if record.parent else None,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Operation_refsQuerySet(self.model, using=self._db)


class Operation_refs(AuditModel):
    parent = ForeignKeyProtect(Operations, related_name='operation_parent', blank=True, null=True)
    child = ForeignKeyProtect(Operations, related_name='operation_child')
    props = Operation_refsManager.props()

    objects = Operation_refsManager()

    def __str__(self):
        return f"\n\nID:{self.id},\n\n " \
               f"props:{self.props},\n\n " \
               f"child: [{self.child}],\n\n " \
               f"parent: [{self.parent}]"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица операций планирования'
        constraints = [
            CheckConstraint(check=~Q(child=F('parent')), name='Operation_refs_not_circulate_refs'),
            UniqueConstraint(fields=['child', 'props'], condition=Q(deleted_at=None) & Q(parent=None), name='Operation_refs_unique_constraint_0'),
            UniqueConstraint(fields=['child', 'parent', 'props'], condition=Q(deleted_at=None), name='Operation_refs_unique_constraint_1'),

        ]
