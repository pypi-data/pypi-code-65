import logging

from django.core.management import BaseCommand
from django.db import transaction

from kaf_pas.planing.models.operation_refs import Operation_refs

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        operation_refs = Operation_refs.objects.get(id=278450)
        with transaction.atomic():
            Operation_refs.objects.delete_m2m(operation_refs=operation_refs)
