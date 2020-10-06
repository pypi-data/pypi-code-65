import logging

from django.core.management import BaseCommand

from kaf_pas.planing.models.rouning_ext import Route_item

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # print(RoutingManager.make_levels(launch_id=30))
        route_item = Route_item()
        for item in route_item.make_locationsLevel(launch_id=23, level_id=17):
            print(item)
