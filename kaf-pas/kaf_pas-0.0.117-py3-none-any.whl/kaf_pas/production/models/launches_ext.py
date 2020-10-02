import logging

from isc_common import delAttr
from isc_common.common import red

logger = logging.getLogger(__name__)


class Launches_ext:
    def _getQtyChilds(self, records):
        from django.db import connection
        from kaf_pas.ckk.models.item_qty import Item_qty

        res = 0
        if isinstance(records, list):

            with connection.cursor() as cursor:
                for record in records:
                    sql_str = '''WITH RECURSIVE r AS (
                                                        SELECT *, 1 AS level
                                                        FROM production_launch_item_refs
                                                        WHERE parent_id IN (%s)

                                                        union all

                                                        SELECT production_launch_item_refs.*, r.level + 1 AS level
                                                        FROM production_launch_item_refs
                                                                 JOIN r
                                                                      ON production_launch_item_refs.parent_id = r.child_id)

                                                        select  count(*)
                                                        from r where launch_id = %s'''

                    cursor.execute(sql_str, [record.get('id'), record.get('launch_id')])
                    qty, = cursor.fetchone()
                    res += qty
                    Item_qty.objects.create(
                        child_id=record.get('id'),
                        parent_id=record.get('parent_id'),
                        qty=qty
                    )
        return dict(qty=res)

    def get_count(self, item_line, qty, level, get_full_path, items_refs_qty_stack):
        from isc_common import StackElementNotExist
        from isc_common.common import blinkString
        from isc_common.number import StrToNumber
        from kaf_pas.kd.models.document_attributes import Document_attributes
        from kaf_pas.production.models import SPC_CLM_COUNT_ATTR

        # key = 'LaunchesManager.get_count'
        # settings.LOCKS.acquire(key)

        res = None
        if items_refs_qty_stack.size() > 0:

            # qty = items_refs_qty_stack.find_one(lambda x: x[0] == level - 1 and x[1] == get_full_path_obj[level - 1].get('id'))[2]
            parent_items = items_refs_qty_stack.find(lambda x: x[1] == item_line.parent.id)
            if len(parent_items) == 1:
                qty = parent_items[0][2]
            elif len(parent_items) == 0:
                if qty is None:
                    raise StackElementNotExist(blinkString(f'Не удалось получить количество для : {get_full_path}', color=red, bold=True))
            else:
                parent_item = list(reversed(sorted(parent_items, key=lambda x: x[0])))
                qty = parent_item[0][2]

        if level == 1:
            res, _ = Document_attributes.objects.get_or_create(attr_type=SPC_CLM_COUNT_ATTR, value_str=str(qty), value_int=qty)
            # settings.LOCKS.release(key)
            return res

        _str = item_line.SPC_CLM_COUNT.value_str if item_line.SPC_CLM_COUNT else None
        if _str == 'null':
            _str = None

        if _str is not None:
            if _str.find(',') != -1:
                try:
                    str1 = _str.replace(',', '.')
                    count = StrToNumber(str1)

                    SPC_CLM_COUNT, created = Document_attributes.objects.get_or_create(attr_type=SPC_CLM_COUNT_ATTR, value_str=str1)
                    if created == False:
                        SPC_CLM_COUNT.value_int = count
                        SPC_CLM_COUNT.value_str = str1
                        SPC_CLM_COUNT.save()

                    if qty > 1:
                        count *= qty
                        SPC_CLM_COUNT, created = Document_attributes.objects.get_or_create(attr_type=SPC_CLM_COUNT_ATTR, value_str=str(count))
                        if created != True:
                            SPC_CLM_COUNT.value_int = count
                            SPC_CLM_COUNT.save()

                    res = SPC_CLM_COUNT
                except ValueError:
                    SPC_CLM_COUNT, created = Document_attributes.objects.get_or_create(attr_type=SPC_CLM_COUNT_ATTR, value_str='1')
                    if created == True:
                        SPC_CLM_COUNT.value_int = 1
                        SPC_CLM_COUNT.save()

            else:
                try:
                    count = StrToNumber(_str)
                    if qty > 1:
                        count *= qty
                        SPC_CLM_COUNT, created = Document_attributes.objects.get_or_create(attr_type=SPC_CLM_COUNT_ATTR, value_str=str(count))
                        if created == True:
                            SPC_CLM_COUNT.value_int = count
                            SPC_CLM_COUNT.save()
                        res = SPC_CLM_COUNT
                    else:
                        res = item_line.SPC_CLM_COUNT
                except ValueError:
                    SPC_CLM_COUNT, created = Document_attributes.objects.get_or_create(attr_type=SPC_CLM_COUNT_ATTR, value_str='1')
                    if created == True:
                        SPC_CLM_COUNT.value_int = 1
                        SPC_CLM_COUNT.save()

        else:
            res = item_line.SPC_CLM_COUNT

        if res is None and item_line.section != 'Документация':
            raise Exception(blinkString(f'Для: {get_full_path} count == 0', color='red', bold=True, blink=False))

        # settings.LOCKS.release(key)
        return res

    def rec_operation(self, operations_item, launch, get_full_path):
        from django.conf import settings
        from isc_common.common import blinkString
        from kaf_pas.production.models.launch_operation_attr import Launch_operation_attr
        from kaf_pas.production.models.launch_operation_material import Launch_operations_material
        from kaf_pas.production.models.launch_operation_resources import Launch_operation_resources
        from kaf_pas.production.models.launch_operations_item import Launch_operations_item
        from kaf_pas.production.models.operation_attr import Operation_attr
        from kaf_pas.production.models.operation_material import Operation_material
        from kaf_pas.production.models.operation_resources import Operation_resources

        # start_time = time.clock()
        launch_operations_item, created = Launch_operations_item.objects.get_or_create(
            item=operations_item.item,
            launch=launch,
            num=operations_item.num,
            operation=operations_item.operation,
            color=operations_item.color,
            defaults=dict(
                description=operations_item.description,
                ed_izm=operations_item.ed_izm,
                operationitem=operations_item,
                qty=operations_item.qty,
            )
        )

        for operation_attr in Operation_attr.objects.filter(operation=operations_item.operation):
            Launch_operation_attr.objects.get_or_create(
                operation=launch_operations_item.operation,
                launch=launch,
                attr_type=operation_attr.attr_type
            )

        if created:
            # logger.debug(f'Created: {created} launch_operations_item :  {launch_operations_item}')
            # logger_timing.debug(f'launch_operations_item Time: {time.clock() - start_time}')
            pass

            operation_material_query = Operation_material.objects.filter(operationitem=operations_item)

            for operation_material in operation_material_query:
                # start_time = time.clock()
                # 'launch_operationitem', 'material', 'material_askon'
                if operation_material.material is not None or operation_material.material_askon is not None:
                    launch_operations_material, created = Launch_operations_material.objects.get_or_create(
                        launch_operationitem=launch_operations_item,
                        material=operation_material.material,
                        material_askon=operation_material.material_askon,
                        defaults=dict(
                            operation_material=operation_material,
                            edizm=operation_material.edizm,
                            qty=operation_material.qty,
                        )
                    )
                    # launch_operations_materials.push(launch_operations_material)
                    if created:
                        # logger.debug(f'Created: launch_operations_material :  {launch_operations_material}')
                        pass

            def exception_not_location():
                raise Exception(f'''<b>Для : {get_full_path}</b>  {blinkString(text='не задано местоположение. Запустите анализатор готовности к запуску.', blink=False, color='red', bold=True)}''')

            operation_resources_query = Operation_resources.objects.filter(operationitem=operations_item)

            if operation_resources_query.count() == 0:
                exception_not_location()

            for operation_resources in operation_resources_query:
                if operation_resources.location is None:
                    exception_not_location()

                if operation_resources.resource is None:
                    operation_resources.resource, created = settings.OPERS_STACK.NOT_UNDEFINED_WORKSHOP(operation_resources.location)

                if operation_resources.resource_fin is None:
                    operation_resources.resource_fin, created = settings.OPERS_STACK.NOT_UNDEFINED_WORKSHOP(operation_resources.location_fin)

                if operations_item.operation.is_transportation:
                    if operation_resources.resource_fin is None and operation_resources.location_fin is None:
                        raise Exception(f'''<b>Для : {get_full_path}</b>  {blinkString(text=f'в операции {operations_item.operation.full_name} не задано конечное местоположение. Запустите анализатор готовности к запуску.', blink=False, color='red', bold=True)}''')

                launch_operation_resource, created = Launch_operation_resources.objects.get_or_create(
                    launch_operationitem=launch_operations_item,
                    resource=operation_resources.resource,
                    resource_fin=operation_resources.resource_fin,
                    location=operation_resources.location,
                    location_fin=operation_resources.location_fin,
                    defaults=dict(
                        operation_resources=operation_resources,
                        batch_size=operation_resources.batch_size,
                    )
                )
                # launch_operation_resources.push(launch_operation_resource)
                if created:
                    # logger.debug(f'Created: launch_operation_resources.resource :  {launch_operation_resource}')
                    pass

    def rec_operations_data(self, item, section, get_full_path, key, first_step, launch):
        from django.conf import settings
        from isc_common.common import blinkString
        from kaf_pas.production.models.operations_item import Operations_item

        # start_time = time.clock()
        cnt = Operations_item.objects.filter(item=item).count()
        # logger_timing.debug(f'Operations_item.objects.filter Time: {time.clock() - start_time}')
        if cnt == 0:
            if section != 'Документация':
                settings.LOCKS.release(key)
                raise Exception(blinkString(text=f'Для : ID: {item.id} {get_full_path} не найдена операция.', bold=True, blink=False))
        else:

            if first_step == True and section == 'Документация':
                settings.LOCKS.release(key)
                raise Exception(blinkString(text=f'Изделие : ID: {item.id} {get_full_path} должно входить как сборочная Единица.', bold=True, blink=False))

            if section != 'Документация':
                operations_item_query = Operations_item.objects.filter(item=item)

                for operations_item in operations_item_query:
                    try:
                        if (operations_item.ed_izm is not None and operations_item.qty is None) or \
                                (operations_item.ed_izm is None and operations_item.qty is not None):
                            operations_item.ed_izm = None
                            operations_item.qty = None
                            operations_item.save()

                        self.rec_operation(operations_item=operations_item, launch=launch, get_full_path=get_full_path)
                    except Exception as ex:
                        settings.LOCKS.release(key)
                        raise ex

    def rec_launch(self, mode, date, description, key, user, qty=None, item=None, parentlaunch=None, demand=None):
        from django.conf import settings
        from django.db import transaction
        from isc_common import Stack
        from isc_common.bit import TurnBitOn
        from isc_common.common import blinkString
        from isc_common.datetime import DateToStr
        from isc_common.number import StrToNumber
        from isc_common.progress import managed_progress
        from isc_common.progress import progress_deleted
        from isc_common.progress import ProgressDroped
        from kaf_pas.ckk.models.ed_izm import Ed_izm
        from kaf_pas.ckk.models.item_line import Item_line
        from kaf_pas.ckk.models.item_refs import Item_refs
        from kaf_pas.production.models import p_id
        from kaf_pas.production.models.launch_item_line import Launch_item_line
        from kaf_pas.production.models.launch_item_refs import Launch_item_refs
        from kaf_pas.production.models.launches import Launches
        from kaf_pas.production.models.ready_2_launch_ext import Item_refs_Stack
        from kaf_pas.production.models.launches_view import Launches_viewManager

        edizm_shtuka = Ed_izm.objects.get(code='шт')

        if mode == 'update':
            if demand is not None:
                item_query = Launches.objects.filter(demand=demand, status__code='formirovanie')
                item_count = item_query.count()
                if item_count > 0:
                    settings.LOCKS.release(key)
                    raise Exception(f'{demand.code} от {DateToStr(demand.lastmodified)} уже включен в данный запуск.')

        if demand is not None:
            cnt = Launches.objects.filter(demand=demand).count() + 1
            child_code = f'{demand.code}/{cnt}'
        else:
            cnt = Launches.objects.filter(parent=parentlaunch).count() + 1
            child_code = f'{parentlaunch.code} / {cnt}'

        logger.debug(f'cnt: {cnt}')
        # logger.debug(f'child_code: {child_code}')

        if demand is not None:
            where_clause = f'where is_bit_on(props, 0) = true \n' \
                           f'-- and is_bit_on(props, 1) = true \n' \
                           f'and parent_id != {p_id}'

            cntAll = Item_refs.objects.get_descendants_count(
                id=demand.precent_item.item.id,
                where_clause=where_clause,
            )
        else:
            where_clause = f'where is_bit_on(props, 0) = true \n' \
                           f'-- and is_bit_on(props, 1) = true \n'

            cntAll = Item_refs.objects.get_descendants_count(
                id=item.id,
                where_clause=where_clause,
                distinct='distinct',
                limit1=1
            )

        logger.debug(f'cntAll: {cntAll}')
        first_step = True

        def get_template(date):
            from isc_common.datetime import DateToStr
            return DateToStr(date, '%Y / %m')

        if mode == 'add':
            code = get_template(date)
            num = len([code for code in [get_template(launch.date) for launch in Launches.objects.filter(parent__isnull=True)] if code == code]) + 1
            code = f'''{code} / {num}'''
        elif mode == 'update':
            code = parentlaunch.code
        else:
            settings.LOCKS.release(key)
            raise Exception(f'Unknown mode: {mode}')

        if demand is not None:
            message = blinkString(f'Формирование производственной спецификации: <br>Запуск № {code}, <br>Заказ № {demand.code} от {DateToStr(demand.date)} ({cntAll} позиций.)', bold=True, blink=False)
        else:
            message = blinkString(f'Формирование производственной спецификации: <br>Запуск № {child_code}, от {DateToStr(date)} <br>Изделие: {item.item_name} ({cntAll} позиций.)</pre>', bold=True, blink=False)

        with managed_progress(
                id=f'demand_{demand.id}_{user.id}' if demand is not None else f'demand_{item.id}_{user.id}',
                qty=cntAll,
                user=user.id,
                message=message,
                title='Выполнено',
                props=TurnBitOn(0, 0)
                # props=TurnBitOn(0, 1) #Без WebSocket progressbar a
        ) as progress:
            with transaction.atomic():
                def except_func():
                    settings.LOCKS.release(key)

                progress.except_func = except_func

                qty = demand.qty if demand is not None else qty

                if mode == 'add':
                    if parentlaunch is None:
                        parentlaunch = Launches.objects.create(
                            date=date,
                            code=code,
                            description=description,
                            status=settings.PROD_OPERS_STACK.FORMIROVANIE
                        )

                launch = Launches.objects.create(
                    parent=parentlaunch,
                    code=child_code,
                    date=date,
                    demand=demand if demand is not None else None,
                    item=item if item is not None else demand.precent_item.item,
                    description=description,
                    qty=qty,
                    status=settings.PROD_OPERS_STACK.FORMIROVANIE
                )

                items_refs_stack = Item_refs_Stack()
                items_refs_qty_stack = Stack()
                items_refs_not_used = Stack()

                if demand is not None:
                    items_refs_stack.add_parents(id=demand.precent_item.item.id)
                    item_ref_query = Item_refs.objects.get_descendants(
                        id=demand.precent_item.item.id,
                        where_clause=where_clause
                    )
                else:
                    # items_refs_stack.add_parents(id=item.id)
                    item_ref_query = Item_refs.objects.get_descendants(
                        id=item.id,
                        where_clause=where_clause,
                        distinct='distinct',
                        limit1=1
                    )

                for item_ref in item_ref_query:
                    if ~item_ref.props.used:
                        items_refs_not_used.push(item_ref, lambda _: items_refs_not_used.exists(lambda _item_ref: item_ref.child.id == _item_ref.child.id))
                        continue

                    _continue = False
                    for _items_ref in items_refs_not_used.find(lambda _item_ref: item_ref.parent.id == _item_ref.child.id):
                        items_refs_not_used.push(item_ref, lambda _: items_refs_not_used.exists(lambda _item_ref: item_ref.child.id == _item_ref.child.id))
                        _continue = True
                        break

                    if _continue:
                        continue

                    items_refs_stack.push(item_ref)
                    item_line = None

                    try:
                        item_line = Item_line.objects.get(parent=item_ref.parent, child=item_ref.child)
                        # logger.debug(f'item_line: {item_line}')

                    except Item_line.DoesNotExist:
                        if demand is not None:
                            settings.LOCKS.release(key)
                            raise Exception(blinkString(text=f'Для : PARENT_ID: {item_ref.parent.id if item_ref.parent else None} CHILD_ID: {item_ref.child.id} {items_refs_stack.get_full_path} не найдена строка детализации.', bold=True, blink=False))

                    if item_line is not None:
                        count = self.get_count(
                            item_line=item_line,
                            qty=demand.qty if demand is not None else qty,
                            level=item_ref.level,
                            get_full_path=items_refs_stack.get_full_path,
                            items_refs_qty_stack=items_refs_qty_stack
                        )

                        _count_per_one = StrToNumber(item_line.SPC_CLM_COUNT.value_str) if count is not None and item_line.section != 'Документация' else 0
                        _count = StrToNumber(count.value_str) if count is not None and item_line.section != 'Документация' else 0

                        if items_refs_qty_stack.exists(lambda x: x[0] == item_ref.level and x[1] == item_ref.child.id) == False:
                            items_refs_qty_stack.push((item_ref.level, item_ref.child.id, _count))
                    else:
                        _count = qty
                        _count_per_one = 1

                    # start_time = time.clock()
                    logger.debug('//////////////////////////')
                    logger.debug(f'parent: {item_ref.parent.item_name if item_ref.parent else None}, child: {item_ref.child.item_name}, qrt: {_count}, qty_per_one: {_count_per_one}')
                    logger.debug('//////////////////////////')

                    launch_item_refs, created = Launch_item_refs.objects.get_or_create(
                        child=item_ref.child,
                        parent=item_ref.parent if item_ref.level != 1 else None,
                        launch=launch,
                        defaults=dict(
                            item_refs=item_ref,
                            qty=_count,
                            qty_per_one=_count_per_one,
                            item_full_name=items_refs_stack.get_full_path,
                            item_full_name_obj=items_refs_stack.get_full_path_obj
                        )
                    )

                    if created:
                        # logger.debug(f'Created: {created} launch_item_refs :  {launch_item_refs}')
                        # logger_timing.debug(f'launch_item_refs Time: {time.clock() - start_time}')
                        pass

                    else:
                        launch_item_refs.replication_factor += 1
                        launch_item_refs.save()
                        # logger.warning(f'!!!!!!!!!!!!!!!!!!!!!!!!!!!! Not Created: {created} launch_item_refs :  {launch_item_refs} !!!!!!!!!!!!!!!!!!!!!!!')

                        # start_time = time.clock()

                    edizm = item_line.edizm if item_line is not None and item_line.edizm else edizm_shtuka

                    launch_item_line = None

                    if item_line is not None:
                        launch_item_line, created = Launch_item_line.objects.get_or_create(
                            child=item_line.child,
                            parent=item_line.parent,
                            launch=launch,

                            defaults=dict(
                                item_line=item_line,
                                SPC_CLM_FORMAT=item_line.SPC_CLM_FORMAT,
                                SPC_CLM_ZONE=item_line.SPC_CLM_ZONE,
                                SPC_CLM_POS=item_line.SPC_CLM_POS,
                                SPC_CLM_MARK=item_line.SPC_CLM_MARK,
                                SPC_CLM_NAME=item_line.SPC_CLM_NAME,
                                SPC_CLM_COUNT=count,
                                SPC_CLM_NOTE=item_line.SPC_CLM_NOTE,
                                SPC_CLM_MASSA=item_line.SPC_CLM_MASSA,
                                SPC_CLM_MATERIAL=item_line.SPC_CLM_MATERIAL,
                                SPC_CLM_USER=item_line.SPC_CLM_USER,
                                SPC_CLM_KOD=item_line.SPC_CLM_KOD,
                                SPC_CLM_FACTORY=item_line.SPC_CLM_FACTORY,
                                edizm=edizm,
                                section=item_line.section,
                                section_num=item_line.section_num,
                                subsection=item_line.subsection,
                            )
                        )

                        if created:
                            logger.debug(f'Created : launch_item_line :  {launch_item_line}')
                            pass
                        else:
                            logger.debug(f'Existed : launch_item_line :  {launch_item_line}')

                    section = launch_item_line.section if launch_item_line is not None else 'Нет'
                    if item_ref.parent:
                        if first_step == False and demand is not None:
                            self.rec_operations_data(
                                item=item_ref.parent,
                                section=section,
                                get_full_path=items_refs_stack.get_full_path,
                                key=key,
                                first_step=first_step,
                                launch=launch,
                            )

                    self.rec_operations_data(
                        item=item_ref.child,
                        section=section,
                        get_full_path=items_refs_stack.get_full_path,
                        key=key,
                        first_step=first_step,
                        launch=launch,
                    )
                    first_step = False

                    if progress.step() != 0:
                        settings.LOCKS.release(key)
                        raise ProgressDroped(progress_deleted)

                if demand is not None:
                    demand.status = settings.PROD_OPERS_STACK.DEMAND_LAUNCHED
                    demand.save()
                settings.LOCKS.release(key)

                Launches_viewManager.fullRows()

            # end_time = time.clock()
            # logger_timing.debug(f'End Time: {end_time}')
            # logger_timing.debug(f'Total Time: {end_time - start_time}')

            settings.EVENT_STACK.EVENTS_PRODUCTION_MAKE_LAUNCH.send_message(message=f'Выполнено формирование запуска  <h3>{launch.code} от {launch.date}</h3><p/>')
            return parentlaunch, launch

    def make_launch(self, data, mode='add'):
        from django.conf import settings
        from isc_common.datetime import DateTimeToStr
        from isc_common.datetime import DateToStr
        from isc_common.datetime import StrToDate
        from kaf_pas.sales.models.demand import Demand
        from kaf_pas.sales.models.demand_view import Demand_view
        from kaf_pas.production.models.launches import Launches

        logger.debug(f'make_launch data: {data}')
        demands = data.get('demand')

        description = data.get('description')
        date = data.get('date')

        user = data.get('user')
        id = data.get('id')
        parentlaunch = Launches.objects.get(id=id) if id is not None else None

        date = StrToDate(date)
        delAttr(data, 'user')

        if isinstance(demands, list):
            for demand_id in demands:
                demand = Demand_view.objects.get(id=demand_id)
                # if demand.qty_for_launch is None or demand.qty_for_launch == 0:
                #     raise Exception(f'Не указано количестово для запуска заказа № {demand.code} от {DateToStr(demand.date, hours=3)}')
                # elif demand.qty_for_launch > demand.tail_qty:
                #     raise Exception(f'Затребован болшее количество ({demand.qty_for_launch}) количестово для запуска заказа № {demand.code} от {DateToStr(demand.date, hours=3)}, чем имеется в наличии ({demand.tail_qty})')

                if demand.qty > demand.tail_qty:
                    raise Exception(f'Затребовано болшее количество ({demand.qty}) имеется для запуска заказа № {demand.code} от {DateToStr(demand.date, hours=3)}, чем имеется в наличии ({demand.tail_qty})')

        if isinstance(demands, list):
            for demand_id in demands:
                key = f'LaunchesManager.make_launch_{demand_id}'
                settings.LOCKS.acquire(key)
                for demand in Demand.objects.filter(id=demand_id):
                    if demand.status.code != 'otkryt':
                        demand_view = Demand_view.objects.get(id=demand.id)
                        if demand_view.launch_qty == 0:
                            demand.status = settings.PROD_OPERS_STACK.DEMAND_OTKR
                            demand.save()
                        else:
                            settings.LOCKS.release(key)
                            raise Exception(f'Заказ № {demand.code} от {DateTimeToStr(demand.date)} не может быть запущен, т.к. находится в состоянии "{demand.status.name}"')

                    parentlaunch, _ = self.rec_launch(
                        mode=mode,
                        date=date,
                        description=description,
                        user=user,
                        parentlaunch=parentlaunch,
                        key=key,
                        demand=demand,
                    )

        return data
