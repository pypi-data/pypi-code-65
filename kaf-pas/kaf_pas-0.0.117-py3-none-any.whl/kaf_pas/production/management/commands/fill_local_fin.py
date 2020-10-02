import logging

from django.core.management import BaseCommand
from django.db import transaction
from tqdm import tqdm

from kaf_pas.production.models.operation_def_resources import Operation_def_resources
from kaf_pas.production.models.operation_resources import Operation_resources
from kaf_pas.production.models.operations_item import Operations_item
from kaf_pas.production.models.operations_template_detail import Operations_template_detail
from kaf_pas.production.models.operations_template_resource import Operations_template_resource

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Тестирование"

    def handle(self, *args, **options):

        with transaction.atomic():
            pbar = tqdm(total=Operations_item.objects.count())

            for operations_item in Operations_item.objects.all():
                for operation_resources in Operation_resources.objects.filter(operationitem=operations_item):
                    try:
                        operation_def_resources = Operation_def_resources.objects.get(
                            operation=operations_item.operation,
                        )

                        if operation_def_resources.location_fin:
                            operation_resources.location = operation_def_resources.location
                            operation_resources.resource = operation_def_resources.resource
                            logger.debug(f'ИЗ: {operation_def_resources.location}')

                            operation_resources.location_fin = operation_def_resources.location_fin
                            operation_resources.resource_fin = operation_def_resources.resource_fin
                            logger.debug(f'В: {operation_def_resources.location_fin}')
                            operation_resources.save()
                    except Operation_def_resources.DoesNotExist:
                        pass
                pbar.update()
            pbar.close()

            for operations_template_detail in Operations_template_detail.objects.all():
                for operation_def_resources in Operation_def_resources.objects.filter(
                        operation=operations_template_detail.operation,
                ):
                    if operation_def_resources.location_fin:
                        for operations_template_resource in Operations_template_resource.objects.filter(template=operations_template_detail.id):
                            operations_template_resource.resource = operation_def_resources.resource
                            operations_template_resource.location = operation_def_resources.location
                            logger.debug(f'ИЗ: {operation_def_resources.location}')

                            operations_template_resource.location_fin = operation_def_resources.location_fin
                            operations_template_resource.resource_fin = operation_def_resources.resource_fin
                            logger.debug(f'В: {operation_def_resources.location_fin}')

                            operations_template_resource.save()

        print('Done')
