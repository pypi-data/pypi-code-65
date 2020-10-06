import logging

from django.core.management import BaseCommand

from kaf_pas.planing.models.production_order import Production_orderManager

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        Production_orderManager.update_redundant_planing_production_order_table(370750)
