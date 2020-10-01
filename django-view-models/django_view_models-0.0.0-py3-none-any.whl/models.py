from django.db import connections, models
from django.db.utils import ConnectionRouter

class ViewModel(models.Model):
    '''
    A model which is not backed by a table, but a view
    '''

    # Subclasses must define one of these
    VIEW_DEFINITION = None
    # view_query, if defined, should be a queryset (or a callable returning a queryset)
    view_query = None

    @classmethod
    def get_view_definition(cls):
        if cls.VIEW_DEFINITION :
            return cls.VIEW_DEFINITION

        definition = getattr(cls, 'view_query')
        if callable(definition):
            definition = definition()
        return str(definition.query)

    class Meta:
        managed = False
        abstract = True

    @classmethod
    def run_sql(cls, sql):
        '''
        This method is multi-db ready. It uses your site's db router to determine which 
        database the view is in. 
        '''
        db = ConnectionRouter().db_for_read(cls())
        with connections[db].cursor() as cursor :
            cursor.execute(sql)

    @classmethod
    def create_view(cls):
        '''
        Note - CREATE OR REPLACE doesn't always work when renaming/adding columns to a view,
        so we always drop then create
        '''
        cls.run_sql("""
            DROP VIEW IF EXISTS {view_name} CASCADE;
            CREATE VIEW {view_name} AS
            {view_definition};
        """.format(view_name=cls._meta.db_table, view_definition=cls.get_view_definition()))

class MaterializedViewModel(ViewModel):
    class Meta:
        managed = False
        abstract = True

    @classmethod
    def create_view(cls):
        cls.run_sql("""
            DROP MATERIALIZED VIEW IF EXISTS {view_name};
            CREATE MATERIALIZED VIEW {view_name} AS
            {view_definition}
        """.format(view_name=cls._meta.db_table, view_definition=cls.get_view_definition()))

    @classmethod
    def refresh_view(cls):
        cls.run_sql("REFRESH MATERIALIZED VIEW {}".format(cls._meta.db_table))