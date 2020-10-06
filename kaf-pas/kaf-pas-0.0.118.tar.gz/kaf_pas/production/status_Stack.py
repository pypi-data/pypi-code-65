import logging

from django.db import ProgrammingError

logger = logging.getLogger(__name__)

in_production_title = "Сформированы задания на производство"

class Prod_Status_Stack:

    def __init__(self):
        from kaf_pas.ckk.models.attr_type import AttrManager
        from kaf_pas.production.models.status_launch import Status_launch
        from kaf_pas.sales.models.status_demand import Status_demand
        from isc_common.common import new, name_formirovanie, name_handmade, formirovanie

        try:

            self.FORMIROVANIE, _ = Status_launch.objects.update_or_create(code=formirovanie, defaults=dict(
                name=name_formirovanie,
                editing=False,
                deliting=False,
            ))

            self.ROUTMADE, _ = Status_launch.objects.update_or_create(code='route_made', defaults=dict(
                name='Выполнена маршрутизация',
                editing=False,
                deliting=False,
            ))

            self.IN_PRODUCTION, _ = Status_launch.objects.update_or_create(code='in_production', defaults=dict(
                name=in_production_title,
                editing=False,
                deliting=False,
            ))

            self.EXECUTION, _ = Status_launch.objects.update_or_create(code='execution', defaults=dict(
                name='Выполняется',
                editing=False,
                deliting=False,
            ))

            self.CLOSED, _ = Status_launch.objects.update_or_create(code='closed', defaults=dict(
                name='Закрыт',
                editing=False,
                deliting=False,
            ))

            self.HANDMADE, _ = Status_launch.objects.update_or_create(code='handmade', defaults=dict(
                name=name_handmade,
                editing=False,
                deliting=False,
            ))

            self.LAUNCH_NOT_RELEVANT, _ = Status_launch.objects.update_or_create(code='not_relevant', defaults=dict(
                name='Недействительный',
                editing=False,
                deliting=False,
            ))

            AttrManager.get_or_create_attr(attr_codes='operations.paremetrs.color', attr_names='Операции.Параметры.Цвет')

            # DEMAND

            self.DEMAND_OTKR, _ = Status_demand.objects.update_or_create(code='otkryt', defaults=dict(
                name='Открыт',
                editing=False,
                deliting=False,
            ))

            self.DEMAND_NOT_RELEVANT, _ = Status_demand.objects.update_or_create(code='not_relevant', defaults=dict(
                name='Недействительный',
                editing=False,
                deliting=False,
            ))

            self.DEMAND_CLOSED, _ = Status_demand.objects.update_or_create(code='zakryt', defaults=dict(
                name='Закрыт',
                editing=False,
                deliting=False,
            ))

            self.DEMAND_OTMENA, _ = Status_demand.objects.update_or_create(code='otmenen', defaults=dict(
                name='Отменен',
                editing=False,
                deliting=False,
            ))

            self.DEMAND_LAUNCHED, _ = Status_demand.objects.update_or_create(code='launched', defaults=dict(
                name='Запущен',
                editing=False,
                deliting=False,
            ))
            ##

        except ProgrammingError as ex:
            logger.warning(ex)
