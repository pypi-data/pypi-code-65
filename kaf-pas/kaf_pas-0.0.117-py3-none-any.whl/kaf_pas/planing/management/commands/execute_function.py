import logging

from django.core.management import BaseCommand

from isc_common.common.functions import ExecuteStoredProc

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(f'''returned: {ExecuteStoredProc('recStartValue', [10])}''')
