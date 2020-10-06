import logging

from bitfield import BitField

from clndr.models.calendars import Calendars
from isc_common.fields.code_field import CodeField, CodeStrictField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.base_ref import BaseRefHierarcy, BaseRefQuerySet
from isc_common.models.tree_audit import TreeAuditModelManager
from isc_common.number import DelProps

logger = logging.getLogger(__name__)


class LocationsQuerySet(BaseRefQuerySet, CommonManagetWithLookUpFieldsQuerySet):
    pass


class LocationsManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def props():
        return BitField(flags=(
            ('isWorkshop', 'Уровень цеха'),  # 1
        ), default=0, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'full_name': record.full_name,
            'color': record.color,
            'description': record.description,
            'parent_id': record.parent.id if record.parent else None,
            'calendar_id': record.calendar.id if record.calendar else None,
            'calendar__full_name': record.calendar.full_name if record.calendar else None,
            'editing': record.editing,
            'deliting': record.deliting,
            'isWorkshop': record.props.isWorkshop,
            'props': record.props,
        }
        return DelProps(res)

    def get_queryset(self):
        return LocationsQuerySet(self.model, using=self._db)


class Locations(BaseRefHierarcy):
    code = CodeStrictField(unique=True)
    calendar = ForeignKeyProtect(Calendars, null=True, blank=True)
    color = CodeField()
    props = LocationsManager.props()

    objects = LocationsManager()

    objects_tree = TreeAuditModelManager()

    def _get_calendar(self, parent):
        if parent:
            if parent.calendar:
                return parent.calendar
            else:
                return self._get_calendar(parent=parent.parent)
        else:
            return None

    @property
    def is_workshop(self):
        return self.props.isWorkshop.is_set

    @property
    def resource(self):
        from kaf_pas.production.models.resource import Resource
        resource, _ = Resource.objects.get_or_create(location_id=self.id, code='none', defaults=dict(name='Не определен'))
        return resource

    @property
    def get_calendar(self):
        if self.calendar:
            return self.calendar

        return self._get_calendar(parent=self.parent)

    def __repr__(self):
        return self.full_name

    def __str__(self):
        return f"ID: {self.id}, code: {self.code}, name: {self.name}, full_name: {self.full_name}, description: {self.description}"

    class Meta:
        verbose_name = 'Место положения'
