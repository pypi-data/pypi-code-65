from django.contrib.admin.apps import AdminConfig


class PrlAdminConfig(AdminConfig):
    default_site = 'prelude_django_admin_toolkit.admin.PrlAdmin'

