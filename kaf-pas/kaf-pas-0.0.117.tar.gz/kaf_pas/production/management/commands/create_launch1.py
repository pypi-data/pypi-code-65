import logging

from django.core.management import BaseCommand

from isc_common import setAttr
from isc_common.auth.models.user import User
from kaf_pas.production.models.launches_ext import Launches_ext

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Тестирование создание Запуска"

    def handle(self, *args, **options):
        data = {'date': '2020-07-22T06:17:29.835', 'demand': [72]}
        # data =  {'date': '2020-07-22T06:55:55.340', 'demand': [77]}
        setAttr(data, 'user', User.objects.get(id=2))

        launches_ext = Launches_ext()
        return launches_ext.make_launch(data)
