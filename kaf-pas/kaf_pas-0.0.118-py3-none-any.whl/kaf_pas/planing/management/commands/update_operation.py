import logging

from django.core.management import BaseCommand

from isc_common.auth.models.user import User
from kaf_pas.planing.models.production_ext import Production_ext

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # 1 -> Конец

        data = {'creator__short_name': 'admin A A', 'date': '2020-08-07T11:57:03.115', 'parent_id': 344728, 'description': None, 'edizm__name': None, 'enabled': True, 'id': 344729, 'launch_id': 226, 'location_id': 69, 'location__code': '516',
                'location__full_name': '/Завод/Цех №5/Участок мелочевки №2', 'location__name': 'Участок мелочевки №2', 'location_fin_id': None, 'location_fin__code': None, 'location_fin__full_name': None, 'location_fin__name': None, 'num': 344729,
                'production_operation__full_name': '/Цех №5/Слесарно-сборочные/Сборка-сварка', 'production_operation__name': 'Сборка-сварка', 'production_operation_attrs': None, 'production_operation_edizm__name': 'Минута', 'production_operation_edizm_id': 5, 'production_operation_color_id': None,
                'production_operation_color__name': None, 'production_operation_color__color': None, 'production_operation_id': 19, 'production_operation_num': 1, 'production_operation_qty': 10, 'resource__code': 'none', 'resource__description': None, 'resource__name': 'Не определен',
                'resource_id': 201, 'resource_fin__code': None, 'resource_fin__description': None, 'resource_fin__name': None, 'resource_fin_id': None, 'value_sum': '10', 'value_made': '0', 'value1_sum': '2', 'value_start': '', 'isDeleted': False, 'production_operation_is_transportation': False,
                'creator_id': None}

        old_data = {'creator__short_name': 'admin A A', 'date': '2020-08-07T11:57:03.115', 'parent_id': 344728, 'description': None, 'edizm__name': None, 'enabled': True, 'id': 344729, 'launch_id': 226, 'location_id': 69, 'location__code': '516',
                    'location__full_name': '/Завод/Цех №5/Участок мелочевки №2', 'location__name': 'Участок мелочевки №2', 'location_fin_id': None, 'location_fin__code': None, 'location_fin__full_name': None, 'location_fin__name': None, 'num': 344729,
                    'production_operation__full_name': '/Цех №5/Слесарно-сборочные/Сборка-сварка', 'production_operation__name': 'Сборка-сварка', 'production_operation_attrs': None, 'production_operation_edizm__name': None,
                    'production_operation_edizm_id': None, 'production_operation_color_id': None, 'production_operation_color__name': None, 'production_operation_color__color': None, 'production_operation_id': 19, 'production_operation_num': 1,
                    'production_operation_qty': None, 'resource__code': 'none', 'resource__description': None, 'resource__name': 'Не определен', 'resource_id': 201, 'resource_fin__code': None, 'resource_fin__description': None, 'resource_fin__name': None,
                    'resource_fin_id': None, 'value_sum': '10', 'value_made': '0', 'value1_sum': '2', 'value_start': '', 'isDeleted': False, 'production_operation_is_transportation': False, 'creator_id': None}

        production_ext = Production_ext()
        production_ext.update_operation(data=data, old_data=old_data, user=User.objects.get(id=2))

        print('Done.')
