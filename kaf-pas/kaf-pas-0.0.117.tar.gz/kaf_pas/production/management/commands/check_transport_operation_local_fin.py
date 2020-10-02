import logging

from django.core.management import BaseCommand
from django.db import transaction
from tqdm import tqdm

from kaf_pas.production.models.operations import Operations
from kaf_pas.production.models.operations_item import Operations_itemManager, Operations_item

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Тестирование"

    def handle(self, *args, **options):

        with transaction.atomic():
            item_query = Operations_item.objects.values('item').distinct()
            qty = item_query.count()
            pbar = tqdm(total=qty)

            errors_set = set()

            for item in item_query:
                operations_item = list(Operations_item.objects.filter(item_id=item.get('item')).order_by('num', 'id'))
                num = 1
                for operation_item in operations_item:
                    if operation_item.num != num:
                        operation_item.num = num
                        operation_item.save()
                    num += 1

                for operation_item in operations_item:
                    if operation_item.operation.props.mask == Operations.props.transportation.mask:
                        Operations_itemManager.check_tansport_operations(
                            operations_item=operations_item,
                            operation_item=operation_item,
                            errors_set=errors_set
                        )
                        # print('tr')
                    pass

                operations_item = list(Operations_item.objects.filter(item_id=item.get('item')).order_by('num', 'id'))
                num = 1
                for operation_item in operations_item:
                    if operation_item.num != num:
                        operation_item.num = num
                        operation_item.save()
                    num += 1
                pbar.update()

            for error in list(errors_set):
                print(error)

            pbar.close()
            print('Done')

        # operation_item = Operations_item.objects.get(id=20949)
        # Operations_itemManager.check_tansport_operations(
        #     operations_item=list(Operations_item.objects.filter(item=operation_item.item).order_by('num')),
        #     operation_item=operation_item
        # )
