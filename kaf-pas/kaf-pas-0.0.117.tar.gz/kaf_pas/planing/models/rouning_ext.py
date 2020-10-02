import logging

from isc_common import Stack
from isc_common.common import new
from isc_common.json import StrToJson

logger = logging.getLogger(__name__)


class Launch_item:
    def __init__(self, row):
        self.id, self.parent_id, self.child_id, self.launch_id, self.qty, self.replication_factor, self.qty_per_one, self.edizm_id, self.level, self.item_full_name, self.item_full_name_obj = row

    def __str__(self):
        return f'id: {self.id}, \n' \
               f'parent_id: {self.parent_id}, \n' \
               f'child_id: {self.child_id}, \n' \
               f'launch_id: {self.launch_id}, \n' \
               f'qty: {self.qty}, \n' \
               f'replication_factor: {self.replication_factor}, \n' \
               f'qty_per_one: {self.qty_per_one}, \n' \
               f'edizm_id: {self.edizm_id}, \n' \
               f'level: {self.level}, \n' \
               f'item_full_name: {self.item_full_name}, \n' \
               f'item_full_name_obj: {self.item_full_name_obj}'


class Route_item():

    def __init__(self, item_id, first_operation, last_operation):
        from kaf_pas.ckk.models.item import Item

        self.item_id = item_id
        self.item = Item.objects.get(id=item_id)
        self.first_operation = first_operation
        self.last_operation = last_operation

    def __str__(self):
        return f'item_id: {[self.item]}, first_operation: [{self.first_operation}], last_operation: [{self.last_operation}]'


class Routing_ext:

    def make_levels(self, launch_id):
        from kaf_pas.planing.models.operation_level_view import Operation_level_view
        from kaf_pas.planing.models.operations_view import Operations_view
        res = [
            dict(
                id=operation.get('level_id'),
                title=operation.get('level__name'),
                prompt=f'''ID: {operation.get('level_id')}, {operation.get('level__code')} : {operation.get('level__name')}'''
            )
            for operation in Operation_level_view.objects.
                filter(
                launch_id=launch_id,
                opers_refs_props__in=[
                    Operations_view.props.inner_routing,
                    Operations_view.props.outer_routing,
                ]
            ).
                order_by('level__code').
                values('level_id', 'level__name', 'level__code').
                distinct()
        ]
        return res

    def make_locationsLevel(self, launch_id, level_id):
        from kaf_pas.ckk.models.locations import Locations
        from kaf_pas.planing.models.operation_location_view import Operation_location_view
        from kaf_pas.planing.models.operations_view import Operations_view

        res = sorted([
            dict(
                id=operation.get('location_id'),
                title=Locations.objects.get(id=operation.get('location_id')).full_name,
                prompt=f'''ID: {operation.get('location_id')}''',
            )
            for operation in Operation_location_view.objects.
                filter(
                launch_id=launch_id,
                opers_refs_props__in=[
                    Operations_view.props.inner_routing,
                    Operations_view.props.outer_routing,
                ],
                level_id=level_id
            ).
                values('location_id', 'location__name').
                distinct()
        ],
            key=lambda x: x['title'])

        return res

    def make_resourcesLevel(self, launch_id, level_id, location_id):
        from kaf_pas.planing.models.operation_resources_view import Operation_resources_view
        from kaf_pas.planing.models.operations_view import Operations_view

        res = sorted([
            dict(
                id=operation.get('resource_id'),
                title=operation.get('resource__name'),
                prompt=f'''ID: {operation.get('resource_id')}, {operation.get('resource__description')}''',
            )
            for operation in Operation_resources_view.objects.
                filter(
                launch_id=launch_id,
                level_id=level_id,
                location_id=location_id,
                props__in=[
                    Operations_view.props.inner_routing,
                    Operations_view.props.outer_routing,
                ],
            ).values('resource_id', 'resource__name', 'resource__description').distinct()
        ],
            key=lambda x: x['title'])

        return res

    def make_routing(self, data):
        from datetime import datetime
        from django.conf import settings
        from django.db import connection
        from django.db import transaction
        from django.forms import model_to_dict
        from isc_common import Stack
        from isc_common import StackElementNotExist
        from isc_common.auth.models.user import User
        from isc_common.bit import TurnBitOn
        from isc_common.common import blinkString
        from isc_common.common.mat_views import create_tmp_mat_view
        from isc_common.common.mat_views import drop_mat_view
        from isc_common.datetime import DateToStr
        from isc_common.progress import managed_progress
        from isc_common.progress import progress_deleted
        from isc_common.progress import ProgressDroped
        from kaf_pas.planing.models.levels import Levels
        from kaf_pas.planing.models.operation_item import Operation_item
        from kaf_pas.planing.models.operation_item_add import Operation_item_add
        from kaf_pas.planing.models.operation_launch_item import Operation_launch_item
        from kaf_pas.planing.models.operation_launches import Operation_launches
        from kaf_pas.planing.models.operation_level import Operation_level
        from kaf_pas.planing.models.operation_material import Operation_material
        from kaf_pas.planing.models.operation_operation import Operation_operation
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.models.operation_resources import Operation_resources
        from kaf_pas.planing.models.operation_value import Operation_value
        from kaf_pas.planing.models.operations import Operations
        from kaf_pas.production.models.launch_operation_material import Launch_operations_material
        from kaf_pas.production.models.launch_operation_resources import Launch_operation_resources
        from kaf_pas.production.models.launch_operations_item import Launch_operations_item
        from kaf_pas.production.models.launches import Launches
        from kaf_pas.ckk.models.ed_izm import Ed_izm
        from kaf_pas.production.models.launches_view import Launches_viewManager
        from kaf_pas.ckk.models.item import Item

        logger.debug(f'data: {data}')

        launch_ids = []
        launches_head = []

        edizm_shtuka = Ed_izm.objects.get(code='шт')

        for launch_id in data.get('data'):
            launches = Launches.objects.filter(parent_id=launch_id)
            if launches.count() > 0:
                launch_ids.extend([item.id for item in launches])
                launches_head.append(Launches.objects.get(id=launch_id))
            else:
                launch_ids.extend([item.id for item in Launches.objects.filter(id=launch_id)])

        user = data.get('user')
        if not isinstance(user, User):
            raise Exception('user must be User instance.')

        if len(launch_ids) == 0:
            raise Exception('Нет входных данных.')

        launch_qty = Launches.objects.filter(id__in=launch_ids).count()

        idx = 0
        launch_res = None
        for launch in Launches.objects.filter(id__in=launch_ids):
            launch_res = launch

            if launch.status == settings.PROD_OPERS_STACK.ROUTMADE:
                continue

            key = f'OperationsManager.make_routing_{launch.id}'
            settings.LOCKS.acquire(key)
            sql_str = f'''with a as (
                                        with recursive r as (
                                            select *,
                                                   1 as level
                                            from production_launch_item_refs
                                            where parent_id is null
                                               and launch_id = {launch.id}
                                               and is_bit_on(props,0) = true
                                            union all
                                            select production_launch_item_refs.*,
                                                   r.level + 1 as level
                                            from production_launch_item_refs
                                                     join r
                                                          on
                                                              production_launch_item_refs.parent_id = r.child_id
                                            where is_bit_on(r.props::int,0) = true
                                            and is_bit_on(production_launch_item_refs.props,0) = true
                                        )

                                        select r1.id,
                                               r1.parent_id,
                                               r1.child_id,
                                               r1.launch_id,
                                               r1.qty,
                                               r1.replication_factor,
                                               r1.qty_per_one,
                                               r1.edizm,
                                               r1.level,
                                               r1.item_full_name,
                                               r1.item_full_name_obj
                                        from (select distinct r.id,
                                                              r.parent_id,
                                                              r.child_id,
                                                              r.launch_id,
                                                              r.item_full_name,
                                                              r.item_full_name_obj,
                                                              r.qty,
                                                              r.replication_factor,
                                                              r.qty_per_one,
                                                              (
                                                                  select plil.section
                                                                  from production_launch_item_line plil
                                                                  where plil.child_id = r.child_id
                                                                    and plil.parent_id = r.parent_id
                                                                    and plil.launch_id = r.launch_id) section,
                                                              (
                                                                  select plil.edizm_id
                                                                  from production_launch_item_line plil
                                                                  where plil.child_id = r.child_id
                                                                    and plil.parent_id = r.parent_id
                                                                    and plil.launch_id = r.launch_id) edizm,
                                                              level
                                              from r
                                                       join ckk_item ci on ci.id = r.child_id
                                              where r.launch_id = {launch.id}
                                              order by level desc) r1
                                        where lower(r1.section) != 'документация'
                                           or r1.parent_id is null
                                    )

                                    select a.id,
                                           a.parent_id,
                                           a.child_id,
                                           a.launch_id,
                                           a.qty,
                                           a.replication_factor,
                                           a.qty_per_one,
                                           a.edizm,
                                           a.level,
                                           a.item_full_name,
                                           a.item_full_name_obj
                                    from a '''

            mat_view_name = create_tmp_mat_view(sql_str=sql_str, indexes=['parent_id', 'child_id'])
            with connection.cursor() as cursor:
                cursor.execute(f'select count(*) from {mat_view_name}')
                count, = cursor.fetchone()

            logger.debug(f'Counted: {count}')

            with managed_progress(
                    id=f'launch_{launch.id}_{user.id}',
                    qty=count * 2,
                    user=user,
                    message=f'<h3>Расчет маршрутизации внутри товарных позиций, Запуск № {launch.code} от {DateToStr(launch.date)}</h3>',
                    title='Выполнено',
                    props=TurnBitOn(0, 0)
            ) as progress:

                with transaction.atomic():
                    def except_func():

                        drop_mat_view(mat_view_name)
                        settings.LOCKS.release(key)

                    progress.except_func = except_func

                    with connection.cursor() as cursor:
                        cursor.execute(f'select max(level), min(level) from {mat_view_name}')
                        rows = cursor.fetchone()
                        min_level, max_level = rows

                        cursor.execute(f'select * from {mat_view_name} order by level desc')
                        rows = cursor.fetchall()

                        routed_items = Stack()

                        for row in rows:
                            def make_oparetions(row, mode='child'):
                                id, parent_id, child_id, launch_id, qty, replication_factor, qty_per_one, edizm_id, level, item_full_name, item_full_name_obj = row

                                # Более низкий уровень в иерархии товарной позиции соответствует более высокому в маршрутизации, т.к. необходимо изготавливать ранньше
                                level = max_level - (level - min_level)
                                logger.debug(f'level: {level}')

                                if mode == 'child':
                                    cursor.execute(f'select * from {mat_view_name} where qty is null and child_id = %s', [child_id])
                                    null_rows = cursor.fetchall()
                                    if len(null_rows) > 0:
                                        nulls_array = []
                                        for null_row in null_rows:
                                            id, parent_id, child_id, launch_id, qty, qty_per_one, level, item_full_name, item_full_name_obj = null_row
                                            nulls_str = f'<b>ID: {id}: {item_full_name}</b>'
                                            nulls_array.append(nulls_str)

                                        nulls_str = f'''{blinkString(text='Не указано количество : ', color='red')}<br><div>{'<br>'.join(nulls_array)}</div>'''
                                        settings.LOCKS.release(key)
                                        raise Exception(nulls_str)

                                    cursor.execute(f'select sum(qty * replication_factor) from {mat_view_name} where child_id = %s and launch_id = %s', [child_id, launch_id])
                                    qty = cursor.fetchone()[0]
                                    logger.debug(f'qty: {qty}')

                                elif mode == 'parent':
                                    if parent_id is not None:
                                        child_id = parent_id

                                if not routed_items.exists(lambda child_item: child_item.item_id == child_id):
                                    income_operation = None
                                    first_operation = None

                                    # Выполняем маршрутизацию внутри товарной позиции согласно порядку выплонения оперций из production
                                    cnt1 = Launch_operations_item.objects.filter(item_id=child_id, launch_id=launch_id).alive().count()
                                    if cnt1 > 0:
                                        for launch_operations_item in Launch_operations_item.objects.filter(item_id=child_id, launch_id=launch_id).order_by('num'):

                                            outcome_operation = Operations.objects.create(
                                                date=datetime.now(),
                                                opertype=settings.OPERS_TYPES_STACK.ROUTING_TASK,
                                                status=settings.OPERS_TYPES_STACK.ROUTING_TASK_STATUSES.get(new),
                                                creator=user
                                            )
                                            logger.debug(f'Created outcome_operation :  {outcome_operation}')

                                            operation_launches = Operation_launches.objects.create(operation=outcome_operation, launch=launch)
                                            logger.debug(f'Created operation_launches :  {operation_launches}')

                                            operation_item = Operation_item.objects.create(
                                                operation=outcome_operation,
                                                item=launch_operations_item.item,
                                            )
                                            logger.debug(f'Created operation_item :  {operation_item}')

                                            if isinstance(item_full_name_obj, str):
                                                item_full_name_obj = StrToJson(item_full_name_obj)

                                            operation_item_add, created = Operation_item_add.objects.get_or_create(
                                                item=launch_operations_item.item,
                                                launch=launch_operations_item.launch,
                                                item_full_name=item_full_name,
                                                defaults=dict(
                                                    item_full_name_obj=item_full_name_obj
                                                )
                                            )
                                            logger.debug(f'Created operation_item_add :  {operation_item_add}')

                                            operation_operation = Operation_operation.objects.create(
                                                color=launch_operations_item.color,
                                                creator=user,
                                                ed_izm=launch_operations_item.ed_izm,
                                                num=launch_operations_item.num,
                                                operation=outcome_operation,
                                                production_operation=launch_operations_item.operation,
                                                qty=launch_operations_item.qty,
                                            )
                                            logger.debug(f'Created operation_operation :  {operation_operation}')

                                            _level, created = Levels.objects.get_or_create(
                                                code=str(level),
                                                defaults=dict(
                                                    name=str(level),
                                                    editing=False,
                                                    deliting=False
                                                ))
                                            if created:
                                                logger.debug(f'Created level :  {_level}')

                                            operation_level = Operation_level.objects.create(operation=outcome_operation, level=_level)
                                            logger.debug(f'Created operation_level :  {operation_level}')

                                            operation_value = Operation_value.objects.create(
                                                operation=outcome_operation,
                                                value=qty_per_one,
                                                edizm_id=edizm_id if edizm_id is not None else edizm_shtuka.id,
                                                props=Operation_value.props.perone
                                            )
                                            logger.debug(f'Created operation_value :  {operation_value}')

                                            operation_value = Operation_value.objects.create(
                                                operation=outcome_operation,
                                                value=qty,
                                                edizm_id=edizm_id if edizm_id is not None else edizm_shtuka.id,
                                            )
                                            logger.debug(f'Created operation_value :  {operation_value}')

                                            for launch_operation_material in Launch_operations_material.objects.filter(launch_operationitem=launch_operations_item):
                                                if launch_operation_material.operation_material is not None:
                                                    operation_material, _ = Operation_material.objects.get_or_create(
                                                        operation=outcome_operation,
                                                        material=launch_operation_material.material,
                                                        material_askon=launch_operation_material.material_askon,
                                                        defaults=dict(
                                                            edizm=launch_operation_material.edizm,
                                                            qty=launch_operation_material.qty,
                                                        )
                                                    )
                                                    logger.debug(f'Created operation_material :  {operation_material}')

                                            def exception_not_resource():
                                                from isc_common.common import blinkString
                                                settings.LOCKS.release(key)
                                                raise Exception(f'''<b>Для : {item_full_name}</b>  {blinkString(text='не задан ресурс.  Запустите анализатор готовности к запуску.', blink=False, color='red', bold=True)}''')

                                            if Launch_operation_resources.objects.filter(launch_operationitem=launch_operations_item).count() == 0:
                                                exception_not_resource()

                                            for launch_operation_resources in Launch_operation_resources.objects.filter(launch_operationitem=launch_operations_item):
                                                operation_resources = Operation_resources.objects.create(
                                                    operation=outcome_operation,
                                                    resource=launch_operation_resources.resource,
                                                    resource_fin=launch_operation_resources.resource_fin,
                                                    location_fin=launch_operation_resources.location_fin
                                                )
                                                logger.debug(f'Created operation_resources :  {operation_resources}')

                                            if income_operation is None:
                                                first_operation = outcome_operation

                                            operation_refs = Operation_refs.objects.create(
                                                parent=income_operation,
                                                child=outcome_operation,
                                                props=Operation_refs.props.inner_routing,
                                                enable_parent_None=True
                                            )
                                            logger.debug(f'Created operation_refs :  {operation_refs}')

                                            operation_launch_item, created = Operation_launch_item.objects.get_or_create(
                                                operation=outcome_operation,
                                                launch_item=launch_operations_item,
                                            )
                                            if created:
                                                logger.debug(f'Created operation_launch_item :  {operation_launch_item}')

                                            income_operation = outcome_operation
                                            cnt1 -= 1
                                            if cnt1 == 0:
                                                routed_items.push(Route_item(item_id=child_id, first_operation=first_operation, last_operation=outcome_operation), logger=logger)
                                    else:
                                        def exception_not_operations():
                                            from isc_common.common import blinkString
                                            settings.LOCKS.release(key)
                                            raise Exception(f'''<b>Для : {item_full_name}</b>  {blinkString(text='не задано ни одной операции. Запустите анализатор готовности к запуску.', blink=False, color='red', bold=True)}''')

                                        exception_not_operations()

                            make_oparetions(row=row)

                            if progress.step() != 0:
                                settings.LOCKS.release(key)
                                Launches_viewManager.fullRows()
                                raise ProgressDroped(progress_deleted)

                        # Выполняем маршрутизацию между товарными позициями соединяя последнюю оперцию предыдущей товарной позиции с первой операциеей следующей
                        # товарной позиции
                        progress.setContentsLabel(f'<h3>Расчет маршрутизации между товарными позициями, Запуск № {launch.code} от {DateToStr(launch.date)}</h3>')

                        for row in rows:
                            id, parent_id, child_id, launch_id, qty, replication_factor, qty_per_one, edizm_id, level, item_full_name, item_full_name_obj = row
                            try:
                                if parent_id is None:
                                    parent_id = child_id
                                parent_item = routed_items.find_one(lambda item: item.item_id == parent_id)
                            except StackElementNotExist:
                                message = f'{Item.objects.get(id=parent_id).item_name} (ID={parent_id}),  не обнаружена среди товарных позиций, прошедших внутреннюю маршрутизацию. Запустите анализатор готовности,и проверьте какая-то сборочная Единица стоит в разделе документации.'
                                mess2 = ''
                                operation_item_add = Operation_item_add.objects.filter(item_id=child_id)
                                if operation_item_add.count() > 0:
                                    mess2 = f'{operation_item_add[0].item_full_name}'
                                raise Exception(f'{message}\n{mess2}')
                                # Если товарная позиция не обнаружена среди товарных позиций, прошедших внутреннюю маршрутизацию

                                make_oparetions(row=row, mode='parent')
                                parent_item = routed_items.find_one(lambda item: item.item_id == parent_id)

                            cursor.execute(f'''select child_id from {mat_view_name} where parent_id = %s''', [parent_id])
                            parents_rows = cursor.fetchall()
                            for parents_row in parents_rows:
                                _child_id, = parents_row
                                _child = routed_items.find_one(lambda item: item.item_id == _child_id)

                                operation_refs, created = Operation_refs.objects.get_or_create(
                                    parent=_child.last_operation,
                                    child=parent_item.first_operation,
                                    defaults=dict(
                                        props=Operation_refs.props.outer_routing
                                    )
                                )
                                logger.debug(f'Created operation_refs :  {operation_refs}')

                                deleted, _ = Operation_refs.objects.filter(parent__isnull=True, child=parent_item.last_operation).delete()
                            if progress.step() != 0:
                                settings.LOCKS.release(key)
                                raise ProgressDroped(progress_deleted)

                    launch.status = settings.PROD_OPERS_STACK.ROUTMADE
                    launch.save()

                    settings.EVENT_STACK.EVENTS_PRODUCTION_MAKE_ROUTING.send_message(
                        f'<h3>Выполнен Расчет маршрутизации: Запуск № {launch.code} от {DateToStr(launch.date)}</h3><p/>'
                    )

                    Launches_viewManager.refreshRows(ids=launch.id)
                    settings.LOCKS.release(key)
                    drop_mat_view(mat_view_name)

                    idx += 1
                    if idx == launch_qty:
                        for launche_head in launches_head:
                            launche_head.status = settings.PROD_OPERS_STACK.ROUTMADE
                            launche_head.save()

                            # print(LaunchesManager.getRecord(launche_head))
                            Launches_viewManager.refreshRows(ids=launche_head.id)

        return model_to_dict(launch_res)

    def update_materials(self, updated_launch_operations_item, new_operation):
        from kaf_pas.planing.models.operation_material import Operation_material
        from kaf_pas.production.models.launch_operation_material import Launch_operations_material

        operation_materials_set = set()
        for launch_operations_material in Launch_operations_material.objects.filter(launch_operationitem=updated_launch_operations_item):
            logger.debug(f'launch_operations_material :  {launch_operations_material}')

            operation_material, created = Operation_material.objects.update_or_create(
                operation=new_operation,
                material=launch_operations_material.material,
                material_askon=launch_operations_material.material_askon,
                edizm=launch_operations_material.edizm,
                qty=launch_operations_material.qty
            )
            operation_materials_set.add(operation_material.id)
        # Удаляем лишние
        Operation_material.objects.filter(operation=new_operation).exclude(id__in=list(operation_materials_set)).delete()

    def update_resources(self, updated_launch_operations_item, new_operation):
        from kaf_pas.planing.models.operation_resources import Operation_resources
        from kaf_pas.production.models.launch_operation_resources import Launch_operation_resources

        operation_resources_set = set()
        for launch_operation_resource in Launch_operation_resources.objects.filter(launch_operationitem=updated_launch_operations_item, resource__isnull=False):
            logger.debug(f'\nlaunch_operation_resource :  {launch_operation_resource}')

            operation_resource, created = Operation_resources.objects.update_or_create(
                operation=new_operation,
                resource=launch_operation_resource.resource,
                resource_fin=launch_operation_resource.resource_fin,
                location_fin=launch_operation_resource.location_fin,
            )

            if created:
                logger.debug(f'\nCreated operation_resource :  {operation_resource}')
            else:
                logger.debug(f'\nUpdated operation_resource :  {operation_resource}')

            operation_resources_set.add(operation_resource.id)

        # Удаляем лишние
        for operation_resource in Operation_resources.objects.filter(operation=new_operation).exclude(id__in=list(operation_resources_set)):
            logger.debug(f'\nNot used operation_resource :  {operation_resource}')
            operation_resource.delete()

    def print_operation_block(self, launch_id, item_id):
        from django.db import connection
        sql_str = '''select *
                    from (SELECT (
                                     select array_agg(porf.parent_id)
                                     from planing_operation_refs porf
                                              join planing_operations po on porf.parent_id = po.id
                                     where porf.child_id = poli.operation_id
                                       and porf.parent_id is not null
                                       and po.opertype_id = 3
                                       and porf.deleted_at is null
                                 )                      parent_ids,
                                 prdo.id,
                                 poli.operation_id,
                                 num,
                                 prdo.operation_id,
                                 (select array_agg(porf.child_id)
                                  from planing_operation_refs porf
                                           join planing_operations po on porf.child_id = po.id
                                  where porf.parent_id = poli.operation_id
                                  and porf.deleted_at is null
                                    and po.opertype_id = 3
                                 )                      child_ids
                          FROM production_launch_operations_item prdo
                                   join planing_operation_launch_item poli on prdo.id = poli.launch_item_id
                          WHERE (prdo.item_id = %s AND prdo.launch_id = %s)) as s
                    ORDER BY s.num ASC'''

        with connection.cursor() as cursor:
            cursor.execute(sql_str, [item_id, launch_id])
            parents_rows = cursor.fetchall()
            for row in parents_rows:
                parent_ids, id, operation_id, num, prod_operation_id, child_ids = row
                print(f'parent_ids: {parent_ids}, id: {id}, operation_id: {operation_id}, num: {num}, prod_operation_id: {prod_operation_id}, child_ids: {child_ids}')
                # logger.debug(f'parent_ids: {parent_ids}, id: {id}, operation_id: {operation_id}, num: {num}, prod_operation_id: {prod_operation_id}, child_ids: {child_ids}')

    def get_parents(self, operation):
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.operation_typesStack import RT_TSK

        parents = [a.parent.id for a in Operation_refs.objects.filter(child=operation, parent__opertype__code=RT_TSK, deleted_at__isnull=True)]
        logger.debug(f'parents: {parents}')
        return parents

    def get_childs(self, operation):
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.operation_typesStack import RT_TSK

        childs = [a.child.id for a in Operation_refs.objects.filter(parent=operation, child__opertype__code=RT_TSK, deleted_at__isnull=False)]
        if len(childs) == 0:
            childs = [a.child.id for a in Operation_refs.objects.filter(parent=operation, child__opertype__code=RT_TSK, deleted_at__isnull=True)]
        logger.debug(f'childs: {childs}')
        return childs

    def get_num_operation(self, launch, item, num=None, old_num=None):
        from kaf_pas.planing.models.operation_launch_item import Operation_launch_item
        from kaf_pas.production.models.launch_operations_item import Launch_operations_item

        if num is not None and old_num is not None:
            raise Exception('Оба параметра не могут быть не пустыми')

        if num is None and old_num is None:
            raise Exception('Оба параметра не могут быть пустыми')

        if num is not None:
            launch_operations_item_query = Launch_operations_item.objects.filter(
                launch=launch,
                item=item,
                num=num,
                deleted_at=None
            )
        elif old_num is not None:
            launch_operations_item_query = Launch_operations_item.objects.filter(
                launch=launch,
                item=item,
                old_num=old_num,
                deleted_at=None
            )

        if launch_operations_item_query.count() > 1:
            launch_operations_item = launch_operations_item_query[0]
        elif launch_operations_item_query.count() == 1:
            launch_operations_item = launch_operations_item_query[0]
        else:
            raise Exception('launch_operations_item not found')

        operation = Operation_launch_item.objects.get(launch_item=launch_operations_item).operation
        logger.debug(f'operation: {operation}')
        return operation

    def change_parent(self, new_parents, operation, user):
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.operation_typesStack import RT_TSK

        for operation_ref in Operation_refs.objects.filter(child=operation, parent__opertype__code=RT_TSK):
            logger.debug(f'for delete operation_ref.parent: {operation_ref.parent.id if operation_ref.parent else None}, operation_ref.child: {operation_ref.child.id}')
            operation_ref.soft_delete()

        for parent in new_parents:
            if parent != operation.id:
                operation_ref, created = Operation_refs.objects.get_or_create(child=operation, parent_id=parent)
                if created:
                    pass
                    logger.debug(f'created new_operation_ref.parent: {operation_ref.parent.id if operation_ref.parent else None}, new_operation_ref.child: {operation_ref.child.id}')
                else:
                    if operation_ref.deleted_at is not None:
                        operation_ref.soft_restore()

    def change_childs(self, new_childs, operation, user):
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.operation_typesStack import RT_TSK

        for operation_ref in Operation_refs.objects.filter(parent=operation, child__opertype__code=RT_TSK):
            logger.debug(f'for delete operation_ref.parent: {operation_ref.parent.id if operation_ref.parent else None}, operation_ref.child: {operation_ref.child.id}')
            operation_ref.soft_delete()

        for child in new_childs:
            if child != operation.id:
                operation_ref, created = Operation_refs.objects.get_or_create(parent=operation, child_id=child)
                if created:
                    pass
                    logger.debug(f'created new_operation_ref.parent: {operation_ref.parent.id if operation_ref.parent else None}, new_operation_ref.child: {operation_ref.child.id}')
                else:
                    if operation_ref.deleted_at is not None:
                        operation_ref.soft_restore()

    def update_routing(self, data, old_data, updated_launch_operations_items: Stack, user, key=None):
        from kaf_pas.planing.models.operation_launch_item import Operation_launch_item

        logger.debug(f'num: {data.production_operation_num}')
        if old_data is not None:
            logger.debug(f'old_num: {old_data.production_operation_num}')

        for launch_id in list(set([a.launch.id for a in updated_launch_operations_items])):
            lst = sorted([a for a in updated_launch_operations_items if a.launch_id == launch_id], key=lambda x: x.num)
            # for ls in lst:
            #     operation = Operation_launch_item.objects.get(launch_item=ls).operation
            #     logger.debug(f'operation: {operation}')

            max_num = lst[len(lst) - 1].num

            step = 1

            been_is_created = False
            for updated_launch_operations_item in lst:

                # if step == 1:
                #     self.print_operation_block(launch_id=launch_id, item_id=updated_launch_operations_item.item_id)

                new_operation = Operation_launch_item.objects.get(launch_item=updated_launch_operations_item).operation
                logger.debug(f'step: =====================================>>> {step} =============================================>>')
                logger.debug(f'new_operation: {new_operation}')

                self.update_materials(updated_launch_operations_item=updated_launch_operations_item, new_operation=new_operation)
                self.update_resources(updated_launch_operations_item=updated_launch_operations_item, new_operation=new_operation)

                if updated_launch_operations_item.num == updated_launch_operations_item.old_num and not updated_launch_operations_item.is_created:
                    step += 1
                    if step >= max_num:
                        self.print_operation_block(launch_id=launch_id, item_id=updated_launch_operations_item.item_id)
                        pass
                    continue

                logger.debug(f'updated_launch_operations_item.num: {updated_launch_operations_item.num}')
                logger.debug(f'updated_launch_operations_item.old_num: {updated_launch_operations_item.old_num}')

                if not been_is_created:
                    been_is_created = updated_launch_operations_item.is_created

                if updated_launch_operations_item.num == 1:
                    if old_data is not None and data.production_operation_num < old_data.production_operation_num:
                        prev_num_operation = self.get_num_operation(
                            launch=updated_launch_operations_item.launch,
                            item=updated_launch_operations_item.item,
                            num=2
                        )
                    else:
                        prev_num_operation = self.get_num_operation(
                            launch=updated_launch_operations_item.launch,
                            item=updated_launch_operations_item.item,
                            old_num=old_data.production_operation_num if old_data is not None else updated_launch_operations_item.num
                        )
                    parents = self.get_parents(operation=prev_num_operation)
                else:
                    prev_num_operation = self.get_num_operation(
                        launch=updated_launch_operations_item.launch,
                        item=updated_launch_operations_item.item,
                        num=updated_launch_operations_item.num - 1
                    )
                    parents = [prev_num_operation.id]
                logger.debug(f'prev_num_operation: {prev_num_operation}')
                self.change_parent(new_parents=parents, operation=new_operation, user=user)
                # parents = self.get_parents(operation=new_operation)

                if updated_launch_operations_item.num == max_num:
                    if not been_is_created:
                        next_num_operation = self.get_num_operation(
                            launch=updated_launch_operations_item.launch,
                            item=updated_launch_operations_item.item,
                            old_num=updated_launch_operations_item.num  # Правильно, не  менять !!!
                        )
                    else:
                        next_num_operation = self.get_num_operation(
                            launch=updated_launch_operations_item.launch,
                            item=updated_launch_operations_item.item,
                            num=updated_launch_operations_item.num  # Правильно, не  менять !!!
                        )

                    childs = self.get_childs(operation=next_num_operation)
                else:
                    next_num_operation = self.get_num_operation(
                        launch=updated_launch_operations_item.launch,
                        item=updated_launch_operations_item.item,
                        num=updated_launch_operations_item.num + 1
                    )
                    childs = [next_num_operation.id]
                logger.debug(f'next_num_operation: {next_num_operation}')
                self.change_childs(new_childs=childs, operation=new_operation, user=user)
                # childs = self.get_childs(operation=new_operation)

                if step >= max_num:
                    self.print_operation_block(launch_id=launch_id, item_id=updated_launch_operations_item.item_id)
                    pass
                step += 1

    def clean_routing(self, data):
        from django.conf import settings
        from django.db import transaction
        from isc_common.bit import TurnBitOn
        from isc_common.datetime import DateToStr
        from isc_common.progress import managed_progress
        from isc_common.progress import progress_deleted
        from isc_common.progress import ProgressDroped
        from kaf_pas.planing.models.operation_launches import Operation_launches
        from kaf_pas.planing.models.operations import OperationsManager
        from kaf_pas.production.models.launches import Launches
        from kaf_pas.production.models.launches_view import Launches_viewManager
        from isc_common.auth.models.user import User

        launch_ids = []
        launches_head = []

        if not isinstance(data.get('data'), list):
            raise Exception('data must be list')

        for launch_id in data.get('data'):
            launches = Launches.objects.filter(parent_id=launch_id)
            if launches.count() > 0:
                launch_ids.extend([item.id for item in launches])
                launches_head.append(Launches.objects.get(id=launch_id))
            else:
                launch_ids.extend([item.id for item in Launches.objects.filter(id=launch_id)])

        launch_query = Launches.objects.filter(id__in=launch_ids)
        launch_qty = launch_query.count()
        idx = 0

        for launch in launch_query:
            # if launch.status.code == 'formirovanie':
            #     continue

            user = data.get('user')
            if isinstance(user, int):
                user = User.objects.get(id=user)
            elif not isinstance(user, User):
                raise Exception('user must be int or User')

            key = f'OperationsManager.clean_routing_{launch.id}'
            settings.LOCKS.acquire(key)
            query = Operation_launches.objects.filter(launch=launch, operation__opertype__in=[
                settings.OPERS_TYPES_STACK.ROUTING_TASK,
            ])

            cnt = query.count()
            with managed_progress(
                    id=launch.id,
                    qty=cnt,
                    user=user,
                    message=f'<h3>Удаление маршрутизации: Запуск № {launch.code} от {DateToStr(launch.date)}</h3>',
                    title='Выполнено',
                    props=TurnBitOn(0, 0)
            ) as progress:
                with transaction.atomic():
                    def except_func():
                        settings.LOCKS.release(key)

                    progress.except_func = except_func

                    launch.status = launch.status = settings.PROD_OPERS_STACK.FORMIROVANIE
                    launch.save()

                    for operation_launches in query:
                        from kaf_pas.planing.models.operations import Operations
                        try:
                            OperationsManager.delete_recursive(operation=operation_launches.operation, user=user)
                        except Operations.DoesNotExist:
                            pass

                        if progress.step() != 0:
                            settings.LOCKS.release(key)

                            Launches_viewManager.fullRows()
                            raise ProgressDroped(progress_deleted)

                    if cnt > 0:
                        Launches_viewManager.refreshRows(ids=launch.id)
                        settings.EVENT_STACK.EVENTS_PRODUCTION_DELETE_ROUTING.send_message(f'<h3>Выполнено Удаление маршрутизации: Запуск № {launch.code} от {DateToStr(launch.date)}</h3><p/>')

                    settings.LOCKS.release(key)

                    idx += 1

                    if idx == launch_qty:
                        for launche_head in launches_head:
                            launche_head.status = settings.PROD_OPERS_STACK.FORMIROVANIE
                            launche_head.save()

                            Launches_viewManager.refreshRows(ids=launche_head.id)

                        return dict()
