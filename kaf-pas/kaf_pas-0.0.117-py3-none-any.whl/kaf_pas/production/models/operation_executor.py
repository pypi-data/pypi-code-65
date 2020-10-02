import logging

from bitfield import BitField
from django.db import transaction

from isc_common import setAttr
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade, ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from kaf_pas.production.models.operations import Operations

logger = logging.getLogger(__name__)


class Operation_executorQuerySet(AuditQuerySet):
    pass


class Operation_executorManager(AuditManager):

    def createFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        res = []

        # _data = data.copy()
        user_ids = data.get('user_ids')
        context_ids = data.get('context_ids')

        with transaction.atomic():
            for user_id in user_ids:
                for operation_id in context_ids:
                    _data = dict()
                    setAttr(_data, 'user_id', user_id)
                    setAttr(_data, 'operation_id', operation_id)
                    res.append(Operation_executorManager.getRecord(super().get_or_create(**_data)[0]))
        return res

    @staticmethod
    def props():
        return BitField(flags=(
            ('relevant', 'Актуальность'),  # 1
        ), default=1, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
            'user_id': record.user.id,
            'user__username': record.user.username,
            'user__first_name': record.user.first_name,
            'user__last_name': record.user.last_name,
            'user__email': record.user.email,
            'user__middle_name': record.user.middle_name,
        }
        return res

    def get_queryset(self):
        return Operation_executorQuerySet(self.model, using=self._db)


class Operation_executor(AuditModel):
    operation = ForeignKeyCascade(Operations)
    user = ForeignKeyProtect(User, related_name='Production_Operation_executor')
    props = Operation_executorManager.props()

    objects = Operation_executorManager()

    def __str__(self):
        return f"ID:{self.id}, operation: [{self.operation}], user: [{self.user}]"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица ответственных исполнителей'
        unique_together = (('operation', 'user'),)
