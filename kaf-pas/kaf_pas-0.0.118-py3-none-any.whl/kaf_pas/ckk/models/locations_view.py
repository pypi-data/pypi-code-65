import logging

from django.db.models import BooleanField
from django.forms import model_to_dict

from clndr.models.calendars import Calendars
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.base_ref import BaseRefHierarcy, BaseRefQuerySet
from isc_common.models.tree_audit import TreeAuditModelManager
from isc_common.number import DelProps
from kaf_pas.ckk.models.locations import Locations, LocationsManager

logger = logging.getLogger(__name__)


class Locations_viewQuerySet(BaseRefQuerySet, CommonManagetWithLookUpFieldsQuerySet):
    def get_range_rows(self, start=None, end=None, function=None, json=None, distinct_field_names=None, criteria=None, user=None, *args):
        json = self.rearrange_parent(json=json)

        queryResult = self._get_range_rows(*args, start=start, end=end, function=function, json=json, distinct_field_names=distinct_field_names)
        logger.debug(f'\n\n{queryResult.query}\n')

        if function:
            res = [function(record) for record in queryResult]
        else:
            res = [model_to_dict(record) for record in queryResult]

        return res


class Locations_viewManager(CommonManagetWithLookUpFieldsManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'full_name': record.full_name,
            'color': record.color,
            'isFolder': record.isFolder,
            'description': record.description,
            'workshop_id': record.workshop.id if record.workshop else None,
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
        return Locations_viewQuerySet(self.model, using=self._db)


class Locations_view(BaseRefHierarcy):
    calendar = ForeignKeyProtect(Calendars, null=True, blank=True)
    props = LocationsManager.props()
    color = CodeField()
    isFolder = BooleanField()
    workshop = ForeignKeyProtect(Locations, null=True, blank=True)

    objects = Locations_viewManager()

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
    def get_calendar(self):
        if self.calendar:
            return self.calendar

        return self._get_calendar(parent=self.parent)

    def __repr__(self):
        return self.full_name

    def __str__(self):
        return f"ID: {self.id}, code: {self.code}, name: {self.name}, color: {self.color}, full_name: {self.full_name}, description: {self.description}"

    class Meta:
        managed = False
        db_table = 'ckk_locations_view'
        verbose_name = 'Место положения'
