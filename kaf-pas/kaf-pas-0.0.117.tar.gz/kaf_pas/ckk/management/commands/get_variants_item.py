import logging

from django.core.management import BaseCommand

from isc_common.isc.data_binding.advanced_criteria import AdvancedCriteria
from isc_common.isc.data_binding.criteria_stack import CriteriaStack
from isc_common.isc.data_binding.criterion import Criterion
from kaf_pas.ckk.models.item import ItemManager
from kaf_pas.ckk.models.item_view import Item_view
from kaf_pas.production.models.ready_2_launch_ext import Item_refs_Stack

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Тестирование"

    def handle(self, *args, **options):
        logger.info(self.help)

        criteria = [
            {'_constructor': 'AdvancedCriteria', 'operator': 'and', 'criteria':
                [
                    {'fieldName': 'ts', 'operator': 'equals', 'value': 1595890926415},
                    {'fieldName': 'STMP_1__value_str', 'operator': 'iContains', 'value': 'Профиль'},
                    {'fieldName': 'STMP_2__value_str', 'operator': 'iContains', 'value': 'К131.51.01.031'}
                ]},
            {'fieldName': 'parent_id', 'value': None, 'operator': 'notEqual'}
        ]

        res = CriteriaStack(criteria)
        item = dict()

        def get_item(criterion):
            if isinstance(criterion, AdvancedCriteria):
                for criterion in criterion.criteria:
                    if isinstance(criterion, AdvancedCriteria):
                        get_item(criterion=criterion)
                    else:
                        if isinstance(criterion, Criterion):
                            if criterion.fieldName == 'STMP_1__value_str':
                                item['STMP_1'] = criterion.value
                            elif criterion.fieldName == 'STMP_2__value_str':
                                item['STMP_2'] = criterion.value

        for criterion in res:
            get_item(criterion)

        items = ItemManager.find_item1(**item)
        item_refs_Stack = Item_refs_Stack()
        item_refs = [row[0] for row in item_refs_Stack.add_childs(id=[a.id for a in items])]

        print(list(Item_view.objects.filter(refs_id__in=item_refs).distinct()))

        # query = Item.objects.filter(props=Item.props.from_cdw)
        # query = Item_view.objects.filter(from_cdw=True)
        # for item in query:
        #     logger.debug(item)
