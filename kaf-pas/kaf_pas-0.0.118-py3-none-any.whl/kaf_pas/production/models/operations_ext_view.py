import logging

from django.db.models import BooleanField, TextField

from isc_common.fields.name_field import NameField
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.base_ref import BaseRefHierarcy
from isc_common.number import DelProps
from kaf_pas.production.models.operations import OperationsManager

logger = logging.getLogger(__name__)


class Operations_ext_viewQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    pass


class Operations_ext_viewManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            "code": record.code,
            "description": record.description,
            "direction": record.direction,
            "direction_name": record.direction_name,
            "full_name": record.full_name,
            "id": record.id,
            "lastmodified": record.lastmodified,
            "name": record.name,
            "parent_id": record.parent_id,
            'deliting': record.deliting,
            'editing': record.editing,
            'isFolder': record.isFolder,
            'launched': record.props.launched,
            # 'partition_to_launch': record.props.partition_to_launch,
            'props': record.props,
            'transportation': record.transportation,
        }
        return DelProps(res)

    def get_queryset(self):
        return Operations_ext_viewQuerySet(self.model, using=self._db)


class Operations_ext_view(BaseRefHierarcy):
    isFolder = BooleanField()
    transportation = BooleanField()
    props = OperationsManager.get_props()
    direction = NameField()
    direction_name = TextField()

    objects = Operations_ext_viewManager()

    def _get_planing_operation_type(self, parent):
        if parent:
            if parent.planing_operation_type:
                return parent.planing_operation_type
            else:
                return self._get_planing_operation_type(parent=parent.parent)
        else:
            return None

    def __str__(self):
        return f"ID={self.id}, code={self.code}, name={self.name}, description={self.description}"

    class Meta:
        db_table = 'production_operations_ext_view'
        managed = False
        verbose_name = 'Операции'
