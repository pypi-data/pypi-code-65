import logging

from django.db import ProgrammingError

logger = logging.getLogger(__name__)

ACOUNTING = 'ACOUNTING'
CLC_TSK = 'CLC_TSK'
GROUP_TSK = 'GROUP_TSK'
DETAIL_CLC_MNS_TSK = 'DETAIL_CLC_MNS_TSK'
DETAIL_CLC_PLS_TSK = 'DETAIL_CLC_PLS_TSK'
DETAIL_OPERS_PRD_TSK = 'DETAIL_OPERS_PRD_TSK'
DETAIL_SUM_PRD_TSK = 'DETAIL_SUM_PRD_TSK'
LAUNCH_TSK = 'LAUNCH_TSK'
MADE_OPRS_MNS_TSK = 'MADE_OPRS_MNS_TSK'
MADE_OPRS_PLS_TSK = 'MADE_OPRS_PLS_TSK'
MADE_OPRS_PLS_GRP_TSK = 'MADE_OPRS_PLS_GRP_TSK'
PRD_TSK = 'PRD_TSK'
PST_EQV_TSK = 'PST_EQV_TSK'
PST_TSK = 'PST_TSK'
RT_TSK = 'RT_TSK'
WRT_OFF_TSK = 'WRT_OFF_TSK'
NoLaunch = 'Нет'


class Operation_typesStack:

    def __init__(self):
        from kaf_pas.planing.models.operation_types import Operation_types
        from kaf_pas.planing.models.status_operation_types import Status_operation_typesManager
        from kaf_pas.system.models.contants import Contants
        from django.db import transaction
        from isc_common.common import blue, green, new, new_man, started, restarted, transferred, doing, closed, made, deleted, stoped, name_new_h, name_started, name_restarted, name_transferred, name_stoped, name_doing, name_closed, name_new, name_new_s

        try:
            with transaction.atomic():
                Contants.objects.filter(code=ACOUNTING).delete()

                self.PRODUCTION_TASK, _ = Operation_types.objects.update_or_create(code=PRD_TSK, defaults=dict(
                    props=0,
                    name='Задание на производство',
                    editing=False,
                    deliting=False,
                ))

                self.PRODUCTION_TASK_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.PRODUCTION_TASK,
                    status_map=[
                        dict(code=new, name=name_new_s, color=blue),
                        dict(code=new_man, name=name_new_h, color=blue),
                        dict(code=started, name=name_started, color=green),
                        dict(code=restarted, name=name_restarted, color=green),
                        dict(code=transferred, name=name_transferred),
                        dict(code=stoped, name=name_stoped, color='#310062'),
                        dict(code=doing, name=name_doing),
                        dict(code=closed, name=name_closed),
                    ]
                )

                self.PRODUCTION_DETAIL_OPERS_TASK, _ = Operation_types.objects.update_or_create(code=DETAIL_OPERS_PRD_TSK, defaults=dict(
                    props=0,
                    name='Детализация Задания на производство по операциям',
                    editing=False,
                    deliting=False,
                    parent=self.PRODUCTION_TASK
                ))

                self.PRODUCTION_DETAIL_OPERS_TASK_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.PRODUCTION_DETAIL_OPERS_TASK,
                    status_map=[
                        dict(code=new, name=name_new),
                    ]
                )

                self.PRODUCTION_DETAIL_SUM_TASK, _ = Operation_types.objects.update_or_create(code=DETAIL_SUM_PRD_TSK, defaults=dict(
                    props=0,
                    name='Детализация Задания на производство (суммы)',
                    editing=False,
                    deliting=False,
                    parent=self.PRODUCTION_TASK
                ))

                self.PRODUCTION_DETAIL_SUM_TASK_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.PRODUCTION_DETAIL_SUM_TASK,
                    status_map=[
                        dict(code=new, name=name_new),
                    ]
                )

                self.LAUNCH_TASK, _ = Operation_types.objects.update_or_create(code=LAUNCH_TSK, defaults=dict(
                    props=0,
                    name='Запуск задания на производство',
                    editing=False,
                    deliting=False,
                    parent=self.PRODUCTION_TASK
                ))

                self.LAUNCH_TASK_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.LAUNCH_TASK,
                    status_map=[
                        dict(code=new, name=name_new),
                        dict(code=made, name='Выполнен'),
                    ]
                )

                self.GROUP_TASKS, _ = Operation_types.objects.update_or_create(code=GROUP_TSK, defaults=dict(
                    props=Operation_types.props.plus | Operation_types.props.accounting,
                    name='Группировка',
                    editing=False,
                    deliting=False,
                    parent=self.PRODUCTION_TASK
                ))

                self.GROUP_TASKS_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.GROUP_TASKS,
                    status_map=[
                        dict(code=new, name=name_new),
                    ]
                )

                self.MADE_OPERATIONS_PLS_TASK, _ = Operation_types.objects.update_or_create(code=MADE_OPRS_PLS_TSK, defaults=dict(
                    props=Operation_types.props.plus | Operation_types.props.accounting,
                    name='Выполнение прибавляющей производственной операции',
                    editing=False,
                    deliting=False,
                    parent=self.PRODUCTION_TASK
                ))

                self.MADE_OPERATIONS_PLS_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.MADE_OPERATIONS_PLS_TASK,
                    status_map=[
                        dict(code=new, name=name_new),
                    ]
                )

                self.MADE_OPERATIONS_PLS_GRP_TASK, _ = Operation_types.objects.update_or_create(code=MADE_OPRS_PLS_GRP_TSK, defaults=dict(
                    props=Operation_types.props.plus | Operation_types.props.accounting | Operation_types.props.grouping,
                    name='Выполнение прибавляющей производственной операции (с группировочным признаком)',
                    editing=False,
                    deliting=False,
                    parent=self.GROUP_TASKS
                ))

                self.MADE_OPERATIONS_PLS_GRP_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.MADE_OPERATIONS_PLS_GRP_TASK,
                    status_map=[
                        dict(code=new, name=name_new),
                    ]
                )

                self.MADE_OPERATIONS_MNS_TASK, _ = Operation_types.objects.update_or_create(code=MADE_OPRS_MNS_TSK, defaults=dict(
                    props=Operation_types.props.minus | Operation_types.props.accounting,
                    name='Выполнение вычетающей производственной операции',
                    editing=False,
                    deliting=False,
                    parent=self.PRODUCTION_TASK
                ))

                self.MADE_OPERATIONS_MNS_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.MADE_OPERATIONS_MNS_TASK,
                    status_map=[
                        dict(code=new, name=name_new),
                    ]
                )



                self.CALC_TASKS, _ = Operation_types.objects.update_or_create(code=CLC_TSK, defaults=dict(
                    props=0,
                    name='Учет',
                    editing=False,
                    deliting=False,
                ))

                self.CALC_TASKS_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.CALC_TASKS,
                    status_map=[
                        dict(code=new, name=name_new),
                    ]
                )

                self.CALC_DETAIL_PLS_TASK, _ = Operation_types.objects.update_or_create(code=DETAIL_CLC_PLS_TSK, defaults=dict(
                    props=Operation_types.props.plus | Operation_types.props.accounting,
                    name='Детализация Учет приход',
                    editing=False,
                    deliting=False,
                    parent=self.CALC_TASKS
                ))

                self.CALC_DETAIL_PLS_TASK_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.CALC_DETAIL_PLS_TASK,
                    status_map=[
                        dict(code=new, name=name_new),
                    ]
                )

                self.CALC_DETAIL_MNS_TASK, _ = Operation_types.objects.update_or_create(code=DETAIL_CLC_MNS_TSK, defaults=dict(
                    props=Operation_types.props.minus | Operation_types.props.accounting,
                    name='Детализация Учет расход',
                    editing=False,
                    deliting=False,
                    parent=self.CALC_TASKS
                ))

                self.CALC_DETAIL_MNS_TASK_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.CALC_DETAIL_MNS_TASK,
                    status_map=[
                        dict(code=new, name=name_new),
                    ]
                )

                self.POSTING_TASK, _ = Operation_types.objects.update_or_create(code=PST_TSK, defaults=dict(
                    props=0,
                    name='Оприходование',
                    editing=False,
                    deliting=False,
                    parent=self.CALC_TASKS
                ))

                self.POSTING_TASK_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.POSTING_TASK,
                    status_map=[
                        dict(code=new, name=name_new),
                    ]
                )

                self.POSTING_EQV_TASK, _ = Operation_types.objects.update_or_create(code=PST_EQV_TSK, defaults=dict(
                    props=0,
                    name='Оприходование по минусам (выравнивание остатков)',
                    editing=False,
                    deliting=False,
                    parent=self.CALC_TASKS
                ))

                self.POSTING_EQV_TASK_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.POSTING_EQV_TASK,
                    status_map=[
                        dict(code=new, name=name_new),
                    ]
                )

                self.WRITE_OFF_TASK, _ = Operation_types.objects.update_or_create(code=WRT_OFF_TSK, defaults=dict(
                    props=0,
                    name='Списание',
                    editing=False,
                    deliting=False,
                    parent=self.CALC_TASKS
                ))

                self.WRITE_OFF_TASK_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.WRITE_OFF_TASK,
                    status_map=[
                        dict(code=new, name=name_new),
                    ]
                )

                self.ROUTING_TASK, _ = Operation_types.objects.update_or_create(code=RT_TSK, defaults=dict(
                    props=0,
                    name='Маршрутизация',
                    editing=False,
                    deliting=False,
                ))

                self.ROUTING_TASK_STATUSES = Status_operation_typesManager.make_statuses(
                    opertype=self.ROUTING_TASK,
                    status_map=[
                        dict(code=new, name=name_new),
                        dict(code=deleted, name='Удален'),
                    ]
                )

        except ProgrammingError as ex:
            logger.warning(ex)
