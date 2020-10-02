import logging

from django.core.management import BaseCommand

from isc_common.auth.models.user import User
from kaf_pas.planing.models.production_ext import Production_ext

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):

        ids = [345055]
        production_ext = Production_ext()
        production_ext.delete_operation(ids=ids, user=User.objects.get(id=2))

        print('Done.')
