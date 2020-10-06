import logging

from django.core.management import BaseCommand

from isc_common.auth.models.user import User
from kaf_pas.planing.models.production_ext import Production_ext

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        data = {
            'parentRecord': {'creator__short_name': 'Юдин А Г', 'date': '1923-02-10T12:42:33.000', 'description': None, 'edizm__name': 'шт.', 'id': 351035, 'item_id': 3200430, 'parent_item_id': 3185730, 'item__STMP_1__value_str': 'Болт', 'item__STMP_2__value_str': 'К000.39.60.001', 'launch_id': 253,
                             'launch__code': '2020 / 08 / 2', 'launch__date': '2020-08-17T15:33:35.000', 'location_sector_ids': [12, 64, 65, 66, 74],
                             'location_sectors_full_name': '<font color="#CC99FF"</font>/ Завод / Цех №5 / Участок штамповки / Рубка<b> [ выполнено: 12 ]</b><br><font color="#00CCFF"</font>/ Завод / Цех №5 / Токарный участок / Токарная<b> [ выполнено: 10 ]</b><br><font color="#008000"</font>/ Завод / Цех №5 / Инструментальный участок / Термообработка<b> [ выполнено: 10 ]</b><br><font color="#CC99FF"</font>/ Завод / Цех №5 / Участок штамповки / Сверловка<b> [ выполнено: 10 ]</b><br><font color="#808080"</font>/ Завод / Цех №5 / Гальваника / Транспортировка Гальваника (513) - Цех №5(515)<b> [ выполнено: 9 ]</b><br><font color="#808080"</font>/ Завод / Цех №5 / Гальваника / Цинкование<b> [ выполнено: 8 ]</b><br><font color="#000000"</font>/ Завод / Цех №5 / Транспортировка Цех №5 - Гальваника (513)<b> [ выполнено: 8 ]</b>',
                             'num': '7322', 'isFolder': False, 'cnt_opers': 7, 'value_sum': '28', 'value1_sum': '2', 'value1_sum_len': 1, 'value_made': '0', 'value_made_str': '<b><div><strong><font color="blue"</font>8</strong></div></b>(28.57%)', 'value_start': '20', 'value_odd': '20',
                             'opertype__full_name': '/Задание на производство', 'opertype_id': 2, 'parent_id': None, 'status__code': 'new', 'status__name': '<div><strong><font color="green"</font>Запущен</strong></div>', 'status_id': 3, 'isDeleted': False, 'creator_id': None, '_hmarker': None,
                             '_recordComponents_isc_ListGrid_1': {'_rowNumberField': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1}, '_expansionField': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1},
                                                                  'launch__code': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1}, 'launch__date': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1},
                                                                  'num': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1}, 'date': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1},
                                                                  'status__name': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1}, 'item__STMP_1__value_str': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1},
                                                                  'item__STMP_2__value_str': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1}, 'location_sectors_full_name': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1},
                                                                  'cnt_opers': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1}, 'value_sum': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1},
                                                                  'value1_sum': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1}, 'value_start': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1},
                                                                  'value_made_str': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1}, 'edizm__name': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1},
                                                                  'isDeleted': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1}, 'creator__short_name': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1},
                                                                  'description': {'isNullMarker': True, '_embedBody': 'isc_ListGrid_1_body', '_recordComponentBatch': 1}}, '_selection_29': True, '_embeddedComponents_isc_ListGrid_1': ['isc_ListGrid_1_expansionLayout'],
                             '_expanded_isc_ListGrid_1': True, '_hasExpansionComponent_isc_ListGrid_1': True}, 'production_operation__full_name': '/Цех №5/Слесарно-сборочные/Разметка', 'production_operation_edizm__name': None, 'location__full_name': '/Завод/Цех №5/Участок мелочевки №2',
            'production_operation_color__name': None, 'location_fin__full_name': None, 'resource__name': None, 'resource_fin__name': None, 'production_operation_id': 20, 'production_operation_num': 2, 'location_id': 69}

        old_data = None

        production_ext = Production_ext()
        production_ext.update_operation(data=data, old_data=old_data, user=User.objects.get(id=2))

        print('Done.')
