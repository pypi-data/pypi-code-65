import logging

from isc_common.auth.models.user import User
from isc_common.fields.code_field import JSONFieldIVC
from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel

logger = logging.getLogger(__name__)


class Tmp_operation_infoQuerySet(AuditQuerySet):
    pass


class Tmp_operation_infoManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Tmp_operation_infoQuerySet(self.model, using=self._db)


class Tmp_operation_info(AuditModel):
    user = ForeignKeyCascade(User)
    info = JSONFieldIVC()

    objects = Tmp_operation_infoManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Временная информация по работе с операциями'
