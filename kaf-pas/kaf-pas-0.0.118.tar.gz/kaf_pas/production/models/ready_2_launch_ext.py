import logging

from django.db import connection

from isc_common import Stack

logger = logging.getLogger(__name__)


class Item_refs_Stack(Stack):
    def add_parents(self, id, launch_id=None):
        from kaf_pas.ckk.models.item_refs import Item_refs
        from kaf_pas.production.models import p_id

        if isinstance(id, int):
            id = [id]

        if isinstance(id, list):
            id = tuple(id)

        if not isinstance(id, tuple):
            raise Exception('id must be tuple or int')

        if launch_id is None:
            # step = 0
            for item_ref in Item_refs.objects.raw('''select * from (WITH RECURSIVE r AS (
                                                        SELECT *, 1 AS level
                                                        FROM ckk_item_refs
                                                        WHERE child_id IN %s
                                                        and parent_id != %s

                                                        union all

                                                        SELECT ckk_item_refs.*, r.level + 1 AS level
                                                        FROM ckk_item_refs
                                                                 JOIN r
                                                                      ON ckk_item_refs.child_id = r.parent_id)

                                                        select  *
                                                        from r
                                                        where child_id != %s order by level desc) as s
                                                        ''', [id, p_id, p_id]):
                self.push(item_ref)
        else:
            for item_ref in Item_refs.objects.raw('''WITH RECURSIVE r AS (
                                                        SELECT *, 1 AS level
                                                        FROM production_launch_item_refs
                                                        WHERE child_id IN %s

                                                        union all

                                                        SELECT production_launch_item_refs.*, r.level + 1 AS level
                                                        FROM production_launch_item_refs
                                                                 JOIN r
                                                                      ON production_launch_item_refs.child_id = r.parent_id)

                                                    select  *
                                                    from r
                                                    where launch_id = %s order by level desc''', [id, launch_id]):
                self.push(item_ref)

    def add_childs(self, id):
        if isinstance(id, int):
            id = tuple(id)

        if isinstance(id, list):
            id = tuple(id)

        if not isinstance(id, tuple):
            raise Exception('id must be tuple or int')

        if len(id) == 0:
            id = tuple([0])

        with connection.cursor() as cursor:
            cursor.execute('''select *
                            from (WITH RECURSIVE r AS (
                                SELECT id, child_id, parent_id, props, 1 AS level
                                FROM ckk_item_refs
                                WHERE child_id IN %s
                                union all
                                SELECT ckk_item_refs.id, 
                                        ckk_item_refs.child_id, 
                                        ckk_item_refs.parent_id, 
                                        ckk_item_refs.props, 
                                        r.level + 1 AS level
                                FROM ckk_item_refs
                                         JOIN r
                                              ON ckk_item_refs.parent_id = r.child_id)           
                                  select distinct *
                                  from r
                                  order by level) as s''', [id])
            rows = cursor.fetchall()
            return rows

    @property
    def items(self):
        if self.size() == 0:
            return []
        return [item_ref.child.id for item_ref in self.stack]

    @property
    def _get_full_path_obj(self):
        arr = []
        last = self.top()
        if last:
            arr.append(last)
        while True:
            if last.parent is not None:
                last = [item for item in self.stack if item.child.id == last.parent.id]
                if len(last) > 0:
                    last = last[0]
                    arr.append(last)
                else:
                    break
            else:
                # arr.append(last)
                break

        arr = [item for item in reversed(arr)]
        return arr

    @property
    def get_full_path_obj(self):
        from kaf_pas.ckk.models.item_operations_view import Item_operations_view
        from kaf_pas.ckk.models.item_operations_view import Item_operations_viewManager
        arr = [Item_operations_viewManager.getRecord(Item_operations_view.objects.get(refs_id=item.id)) for item in self._get_full_path_obj]
        return arr

    @property
    def get_full_path(self):
        arr = self._get_full_path_obj
        # arr = [item for item in arr if arr.parent is not None]
        if arr[0].parent is not None:
            _arr = [arr[0].parent.item_name]
            _arr.extend([item.child.item_name for item in arr])
            res = ' / '.join(_arr)
        else:
            res = ' / '.join([item.child.item_name for item in arr])
        return '/ ' + res


class Ready_2_launch_ext:
    def make(self, user, ready_2_launch=None, props=32, demand=None, item=None):

        from django.conf import settings
        from django.db import transaction
        from isc_common import Stack
        from isc_common.auth.models.user import User
        from isc_common.bit import IsBitOn, TurnBitOn
        from isc_common.datetime import DateToStr
        from isc_common.progress import managed_progress, ProgressDroped, progress_deleted
        from kaf_pas.ckk.models.item import Item
        from kaf_pas.ckk.models.item_line import Item_line
        from kaf_pas.ckk.models.item_refs import Item_refs
        from kaf_pas.production.models import p_id
        from kaf_pas.production.models.operation_material import Operation_material
        from kaf_pas.production.models.operation_resources import Operation_resources
        from kaf_pas.production.models.operations_item import Operations_item
        from kaf_pas.production.models.ready_2_launch import Ready_2_launch
        from kaf_pas.production.models.ready_2_launch_detail import Ready_2_launch_detail
        from kaf_pas.sales.models.demand import Demand

        if demand is not None and not isinstance(demand, Demand):
            raise Exception('demand must be Demand instance')

        if item is not None and not isinstance(item, Item):
            raise Exception('demand must be Item instance')

        if not isinstance(user, User):
            raise Exception('user must be a User')

        cnt = 0
        cnt_not = 0

        all_notes = Stack()
        options = Stack()

        if IsBitOn(props, 0):
            options.push('Включена опция проверки наличия у операции длительности выполнения.')

        if IsBitOn(props, 1):
            options.push('Включена опция проверки наличия у операции № п/п.')

        if IsBitOn(props, 2):
            options.push('Включена опция проверки наличия у операции материалов или стандартных изделий.')

        if IsBitOn(props, 3):
            options.push('Включена опция проверки наличия у операции ресурса либо места выполнения.')

        if IsBitOn(props, 4):
            options.push('Включена опция проверки наличия у операции единицы измерения.')

        if IsBitOn(props, 5):
            options.push('Включена опция проверки наличия операций.')

        if IsBitOn(props, 6):
            options.push('Включена опция проверки количества.')

        if demand is not None:
            demand_str = f'<h/3>Оценка готовности к запуску: Заказ № {demand.code} от {DateToStr(demand.date)}</h3>'
            key = f'Ready_2_launchManager.make_{demand.id}'
            settings.LOCKS.acquire(key)
            qty = Item_refs.objects.get_descendants_count(
                id=demand.precent_item.item.id,
            )
        else:
            demand_str = f'<h/3>Оценка готовности к запуску: Изделие {item.item_name}</h3>'
            key = f'Ready_2_launchManager.make_{item.id}'
            settings.LOCKS.acquire(key)
            qty = Item_refs.objects.get_descendants_count(id=item.id)

        logger.debug(f'Counted: {qty}')
        with managed_progress(
                id=f'demand_{demand.id}_{ready_2_launch.props}_{user.id}' if demand is not None else f'demand_{item.id}_{ready_2_launch.props}_{user.id}',
                qty=qty,
                user=user,
                message=demand_str,
                title='Выполнено',
                props=TurnBitOn(0, 0)

        ) as progress:
            with transaction.atomic():
                def except_func():
                    settings.LOCKS.release(key)

                progress.except_func = except_func

                items_refs_stack = Item_refs_Stack()
                if not ready_2_launch:
                    if demand is not None:
                        ready_2_launch, _ = Ready_2_launch.objects.get_or_create(demand=demand, item=demand.precent_item.item)
                    else:
                        ready_2_launch, _ = Ready_2_launch.objects.get_or_create(item=item)

                if demand is not None:
                    items_refs_stack.add_parents(demand.precent_item.item.id)
                    descendant_request = Item_refs.objects.get_descendants(id=demand.precent_item.item.id)
                else:
                    items_refs_stack.add_parents(item.id)
                    descendant_request = Item_refs.objects.get_descendants(id=item.id)
                    # descendant_request = Item_refs.objects.get_descendants(id=item.id, where_clause=f'where parent_id != {p_id}')

                for item_ref in descendant_request:

                    # if item_ref.parent and item_ref.parent.id == p_id:
                    #     raise Exception(f'Оценить готовность у {item_ref.child.item_name} невозможно, потому как это позиция находится под {item_ref.parent.item_name}.')

                    notes = Stack()

                    # items_refs_stack.push(item_ref, lambda stack, item: len([it for it in stack if it.id != item_ref.id]) == 0)
                    items_refs_stack.push(item_ref)

                    operations_cnt = Operations_item.objects.filter(item=item_ref.child).alive().count()
                    section = None
                    item_full_name = None
                    item_full_name_obj = None
                    cnt_not1 = 0

                    try:
                        inner_descendant_count = Item_refs.objects.filter(parent=item_ref.child).count()
                        inner_lines_count = Item_line.objects.filter(parent=item_ref.child).count()
                        if inner_descendant_count != inner_lines_count:
                            notes.push(f'Количетво дочерних узлов в дереве состава изделия ({inner_descendant_count}), не равно количеству строк детализации ({inner_lines_count}).')
                            if not item_full_name:
                                item_full_name_obj = items_refs_stack.get_full_path_obj
                                item_full_name = items_refs_stack.get_full_path

                        item_line = None
                        if qty == 1:
                            section = 'Нет'
                        else:
                            item_line = Item_line.objects.get(parent=item_ref.parent, child=item_ref.child)
                            section = item_line.section

                        if section and section != 'Документация':
                            if item_ref.props.used.is_set == False:
                                notes.push('Позиция не используется.')
                                if not item_full_name:
                                    item_full_name_obj = items_refs_stack.get_full_path_obj
                                    item_full_name = items_refs_stack.get_full_path

                            elif IsBitOn(props, 6) and item_line is not None and not item_line.qty:
                                cnt_not1 += 1
                                notes.push('Не указано количество.')
                                if not item_full_name:
                                    item_full_name_obj = items_refs_stack.get_full_path_obj
                                    item_full_name = items_refs_stack.get_full_path
                        else:
                            notes.push('Найдена документация, требует проверки правильности принадлежности.')
                            if not item_full_name:
                                item_full_name_obj = items_refs_stack.get_full_path_obj
                                item_full_name = items_refs_stack.get_full_path

                    except Item_line.DoesNotExist:
                        if demand is not None:
                            cnt_not += 1
                            notes.push('Не входит в детализацию.')
                            if not item_full_name:
                                item_full_name_obj = items_refs_stack.get_full_path_obj
                                item_full_name = items_refs_stack.get_full_path

                    if item_ref.props.used.is_set == True:
                        if section and section != 'Документация':
                            if operations_cnt == 0:
                                if IsBitOn(props, 5):
                                    cnt_not += 1
                                    notes.push('Не указаны операции.')
                                    item_full_name_obj = items_refs_stack.get_full_path_obj
                                    item_full_name = items_refs_stack.get_full_path
                            else:
                                for operations_item in Operations_item.objects.filter(item=item_ref.child):
                                    if IsBitOn(props, 0) and not operations_item.qty:
                                        cnt_not1 = 1
                                        notes.push(f'Операция: {operations_item.operation.full_name} не указана длительность.')
                                        if not item_full_name:
                                            item_full_name_obj = items_refs_stack.get_full_path_obj
                                            item_full_name = items_refs_stack.get_full_path

                                    if IsBitOn(props, 1):
                                        if not operations_item.num:
                                            cnt_not1 = 1
                                            notes.push(f'Операция: {operations_item.operation.full_name} не указан № п/п.')
                                            if not item_full_name:
                                                item_full_name_obj = items_refs_stack.get_full_path_obj
                                                item_full_name = items_refs_stack.get_full_path

                                    if IsBitOn(props, 2):
                                        operation_material_cnt = Operation_material.objects.filter(operationitem=operations_item).count()
                                        if operation_material_cnt == 0:
                                            cnt_not1 = 1
                                            notes.push(f'Операция: {operations_item.operation.full_name} не указаны материалы или стандартные изделия.')
                                            if not item_full_name:
                                                item_full_name_obj = items_refs_stack.get_full_path_obj
                                                item_full_name = items_refs_stack.get_full_path

                                    if IsBitOn(props, 3):
                                        operation_resources_query = Operation_resources.objects.filter(operationitem=operations_item)
                                        if operation_resources_query.count() == 0:
                                            cnt_not1 = 1
                                            notes.push(f'Операция: {operations_item.operation.full_name} не указан ресурс либо место выполнения.')
                                            if not item_full_name:
                                                item_full_name_obj = items_refs_stack.get_full_path_obj
                                                item_full_name = items_refs_stack.get_full_path
                                        else:
                                            from kaf_pas.production.models.operation_def_resources import Operation_def_resources

                                            logger.debug(f'operations_item.operation: {operations_item.operation}')
                                            if operations_item.operation.is_transportation:
                                                operation_resources = operation_resources_query[0]
                                                if operation_resources.location_fin is None and operation_resources.resource_fin is None:

                                                    try:
                                                        operation_def_resources = Operation_def_resources.objects.get(operation=operations_item.operation)
                                                        if operation_def_resources.location_fin is None and operation_def_resources.resource_fin is None:
                                                            cnt_not1 = 1
                                                            notes.push(f'Операция: {operations_item.operation.full_name} не указан конечный ресурс либо место выполнения.')
                                                            if not item_full_name:
                                                                item_full_name_obj = items_refs_stack.get_full_path_obj
                                                                item_full_name = items_refs_stack.get_full_path
                                                        else:
                                                            operation_resources.resource_fin = operation_def_resources.resource_fin
                                                            operation_resources.location_fin = operation_def_resources.location_fin
                                                            operation_resources.save()

                                                    except Operation_def_resources.DoesNotExist:
                                                        cnt_not1 = 1
                                                        notes.push(f'Операция: {operations_item.operation.full_name} не указан конечный ресурс либо место выполнения.')
                                                        if not item_full_name:
                                                            item_full_name_obj = items_refs_stack.get_full_path_obj
                                                            item_full_name = items_refs_stack.get_full_path

                                    if IsBitOn(props, 4) and not operations_item.ed_izm:
                                        cnt_not1 = 1
                                        notes.push(f'Операция: {operations_item.operation.full_name} не указана единица измерения.')
                                        if not item_full_name:
                                            item_full_name_obj = items_refs_stack.get_full_path_obj
                                            item_full_name = items_refs_stack.get_full_path

                    if notes.size() > 0:
                        notes_str = "\n".join(notes)
                        Ready_2_launch_detail.objects.get_or_create(
                            ready=ready_2_launch,
                            notes=notes_str,
                            item_full_name=item_full_name,
                            item_full_name_obj=item_full_name_obj if item_full_name_obj is not None else dict(),
                        )
                    cnt_not += cnt_not1
                    cnt += 1
                    if progress.step() != 0:
                        settings.LOCKS.release(key)
                        raise ProgressDroped(progress_deleted)

                ready = round(100 - cnt_not / cnt * 100, 2)
                all_notes.push(f'{ready}%')
                notes_str = "\n".join(all_notes)
                ready_2_launch.notes = f'<pre>{notes_str}</pre>'
                ready_2_launch.save()

                options_str = "\n" + "\n".join(options)
                settings.EVENT_STACK.EVENTS_PRODUCTION_READY_2_LAUNCH.send_message(f'Выполнена {demand_str} <h3>готовность: {ready} </h3>{options_str}<p/>')
            settings.LOCKS.release(key)
