from django.db import connection


def is_proxy_model_creation_possible() -> bool:
    """
    A proxy model cannot be imported in django when the parent table doesn't exists.
    But algolia django package tries to import the models before the user runs `python manage.py migrate`,
    which throws a django exception.

    In other words this prevents you from creating a database in the first place.
    """
    return 'cms_title' in connection.introspection.table_names()
