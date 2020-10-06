import logging

from django.conf import settings
from django.db import transaction
from django.forms import model_to_dict

from isc_common import delAttr, setAttr
from isc_common.common import new
from isc_common.http.DSRequest import DSRequest
from isc_common.number import DelProps
from kaf_pas.planing.models.operation_resources import Operation_resources
from kaf_pas.planing.models.operations import Operations, OperationsManager, OperationsQuerySet
from kaf_pas.planing.models.operations_view import Operations_view

logger = logging.getLogger(__name__)


class Write_off_itemsQuerySet(OperationsQuerySet):
    pass


class Write_off_itemsManager(OperationsManager):
    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'num': record.num,
            'date': record.date,
            'opertype_id': record.opertype.id,
            'opertype__full_name': record.opertype.full_name,
            'creator__short_name': record.creator.get_short_name,
            'status_id': record.status.id if record.status else None,
            'status__code': record.status.code if record.status else None,
            'status__name': record.status.name if record.status else None,
            'description': record.description,
            'isFolder': False,
        }
        return res

    @staticmethod
    def getRecordDet(record):
        res = {
            'id': record.id,
            'num': record.num,
            'date': record.date,
            'item_id': record.item.id if record.item else None,
            'item__STMP_1_id': record.item.STMP_1.id if record.item and record.item.STMP_1 else None,
            'item__STMP_1__value_str': record.item.STMP_1.value_str if record.item and record.item.STMP_1 else None,
            'item__STMP_2_id': record.item.STMP_2.id if record.item and record.item.STMP_2 else None,
            'item__STMP_2__value_str': record.item.STMP_2.value_str if record.item and record.item.STMP_2 else None,
            'opertype_id': record.opertype.id,
            'opertype__full_name': record.opertype.full_name,
            'creator__short_name': record.creator.get_short_name,
            'status_id': record.status.id if record.status else None,
            'status__code': record.status.code if record.status else None,
            'status__name': record.status.name if record.status else None,
            'resource_id': record.resource.id if record.resource else None,
            'location_id': record.location.id if record.location else None,
            'location__code': record.location.code if record.location else None,
            'location__full_name': record.location.full_name if record.location else None,
            'color_id': record.color.id if record.color else None,
            'color__name': record.color.name if record.color else None,
            'color__color': record.color.color if record.color else None,
            'edizm_id': record.edizm.id if record.edizm else None,
            'edizm__name': record.edizm.name if record.edizm else None,
            'value': record.value,
            'description': record.description,
            'isFolder': False,
        }
        return res

    def createFromRequest(self, request, removed=None):
        from kaf_pas.accounting.models.tmp_buffer import Tmp_buffer
        from kaf_pas.planing.models.operation_color import Operation_color
        from kaf_pas.planing.models.operation_item import Operation_item
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.models.operation_value import Operation_value
        from kaf_pas.planing.models.operation_launches import Operation_launches

        request = DSRequest(request=request)
        data = request.get_data()
        user_id = request.user_id
        parent_id = data.get('parent_id')
        delAttr(data, 'items')
        _data = data.copy()

        delAttr(_data, 'creator__short_name')
        delAttr(_data, 'status__name')
        setAttr(_data, 'opertype', settings.OPERS_TYPES_STACK.WRITE_OFF_TASK)
        setAttr(_data, 'status', settings.OPERS_TYPES_STACK.WRITE_OFF_TASK_STATUSES.get(new))
        setAttr(_data, 'creator_id', user_id)

        with transaction.atomic():
            parent, created = Operations.objects.get_or_create(id=parent_id, defaults=_data)
            if created:
                Operation_refs.objects.create(child=parent,)

            for item in Tmp_buffer.objects.filter(value_off__isnull=False, props=4, user=request.user).exclude(value_off=0):
                child = dict()
                setAttr(child, 'date', parent.date)
                setAttr(child, 'creator_id', user_id)
                setAttr(child, 'description', item.description)
                setAttr(child, 'opertype', settings.OPERS_TYPES_STACK.CALC_DETAIL_MNS_TASK)
                setAttr(child, 'status', settings.OPERS_TYPES_STACK.CALC_DETAIL_MNS_TASK_STATUSES.get(new))
                child = Operations.objects.create(**child)

                Operation_refs.objects.create(parent=parent, child=child)

                if item.item:
                    Operation_item.objects.create(operation=child, item=item.item)

                if item.edizm:
                    Operation_value.objects.create(operation=child, value=item.value_off, edizm=item.edizm)

                if item.color:
                    Operation_color.objects.create(operation=child, color=item.color)

                if item.resource:
                    Operation_resources.objects.create(operation=child, resource=item.resource)

                if item.launch:
                    Operation_launches.objects.create(operation=child, launch=item.launch)

                item.delete()

            parent = model_to_dict(parent)
            return DelProps(parent)

    def get_queryset(self):
        return Write_off_itemsQuerySet(self.model, using=self._db)


class Write_off_items(Operations_view):
    objects = Write_off_itemsManager()

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return self.__str__()

    class Meta:
        proxy = True
        verbose_name = 'Списания'
