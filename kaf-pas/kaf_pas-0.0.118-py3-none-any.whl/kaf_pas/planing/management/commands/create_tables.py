import logging

from django.core.management import BaseCommand

from isc_common.common.mat_views import create_table, create_insert_update_delete_function_of_table

logger = logging.getLogger(__name__)


def create_production_order_tmp_taables():
    tablenames = ['planing_production_order']

    for tablename in tablenames:
        print(f'Creating: {tablename}')

        create_table(
            sql_str=f'''select * from {tablename}_view''',
            table_name=f'''{tablename}_tbl''',
            primary_key=['id'],
            indexes=[
                'id',
                'date',
                'item_id',
                'launch_id',
                'num',
                'isDeleted',
                'opertype_id',
                'parent_id',
                'parent_item_id',
                'props',
                'status_id',
            ]
        )
        print(f'Created: {tablename}')
        print(f'Creating insert_update_delete_function_of_table: {tablename}')

        create_insert_update_delete_function_of_table(table_name=tablename)
        print(f'Created insert_update_delete_function_of_table: {tablename}')

    tablenames = ['planing_production_order_per_launch']

    for tablename in tablenames:
        print(f'Creating: {tablename}')

        create_table(
            sql_str=f'''select * from {tablename}_view''',
            table_name=f'''{tablename}_tbl''',
            primary_key=['id', 'launch_id'],
            indexes=[
                'id',
                'date',
                'item_id',
                'launch_id',
                'num',
                'opertype_id',
                'parent_id',
                'parent_item_id',
                'props',
                'status_id',
            ]
        )

        print(f'Created: {tablename}')
        print(f'Creating insert_update_delete_function_of_table: {tablename}')

        create_insert_update_delete_function_of_table(
            table_name=tablename,
            func_params=[('id', 'bigint'), ('launch_id', 'bigint')],
        )

        print(f'Created insert_update_delete_function_of_table: {tablename}')


class Command(BaseCommand):

    def handle(self, *args, **options):
        create_production_order_tmp_taables()
