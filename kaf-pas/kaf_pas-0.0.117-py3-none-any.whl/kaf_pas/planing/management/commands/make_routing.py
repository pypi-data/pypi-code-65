import logging

from django.core.management import BaseCommand

from kaf_pas.planing.models.levels import Levels
from kaf_pas.planing.models.rouning_ext import Route_item

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for level in Levels.objects.all():
            print('\n\n')
            route_item = Route_item()
            for a in route_item.make_resourcesLevel(launch_id=30, level_id=16, location_id=64):
                print(a)
