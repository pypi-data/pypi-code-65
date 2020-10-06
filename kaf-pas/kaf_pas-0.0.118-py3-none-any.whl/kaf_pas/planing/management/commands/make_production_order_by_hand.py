import logging

from django.core.management import BaseCommand

from isc_common.auth.models.user import User
from kaf_pas.planing.models.production_ext import Production_ext

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        production_ext = Production_ext()
        data = {'launch_id': None, 'launch__code': None, 'launch__date': '2020-07-24T10:49:51.532', 'status__name': 'Новый (р)', 'status_id': 29, 'item__STMP_1__value_str': 'Профиль', 'item__STMP_2__value_str': 'К131.51.01.031', 'location__full_name': '/Завод/Цех №5/Участок мелочевки №2',
                'item_id': 3171231, 'qty': 12, 'location_id': 69, 'description': 'фффвы'}

        # data = {'launch_id': None, 'launch__code': None, 'launch__date': '2020-07-24T10:49:51.532', 'status__name': 'Новый (р)', 'status_id': 29, 'item__STMP_1__value_str': 'Профиль', 'item__STMP_2__value_str': 'К131.51.01.031', 'location__full_name': '/Завод/Цех №5/Участок мелочевки №2',
        #         'item_id': 3171174, 'qty': 12, 'location_id': 69, 'description': 'фффвы'}

        production_ext.make_production_order_by_hand(data=data, user=User.objects.get(id=2))
