import subprocess
import glob
import os

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    @property
    def test_database_name(self):
        return 'test_' + self.database_name

    @property
    def engine(self):
        return settings.DATABASES['default']['ENGINE']

    @property
    def database_name(self):
        return settings.DATABASES['default']['NAME']

    @property
    def database_user(self):
        return settings.DATABASES['default']['USER']

    @property
    def database_pwd(self):
        return settings.DATABASES['default']['PASSWORD']

    def add_arguments(self, parser):
        parser.add_argument('action',  nargs='?')

    def create_user(self):
        if 'postgresql' in self.engine:
            subprocess.call([
                'sudo',
                '-u',
                'postgres',
                'createuser',
                self.database_user,
            ])

            subprocess.call([
                'sudo',
                '-u',
                'postgres',
                'psql',
                '-c',
                "alter user {0} superuser;".format(self.database_user,),
            ])

            subprocess.call([
                'sudo',
                '-u',
                'postgres',
                'psql',
                '-c',
                "alter user {0} with password '{1}';".format(
                    self.database_user,
                    self.database_pwd,
                ),
            ])

    def create(self):
        if 'postgresql' in self.engine:
            subprocess.call([
                'sudo',
                '-u',
                'postgres',
                'createdb',
                self.database_name,
                '-O',
                self.database_user,
            ])

            subprocess.call([
                'sudo',
                '-u',
                'postgres',
                'createdb',
                self.test_database_name,
                '-O',
                self.database_user,
            ])

    def drop(self):
        if 'postgresql' in self.engine:
            subprocess.call([
                'sudo',
                '-u',
                'postgres',
                'dropdb',
                self.database_name
            ])

            subprocess.call([
                'sudo',
                '-u',
                'postgres',
                'dropdb',
                self.test_database_name,
            ])

        elif 'sqlite' in self.engine:
            if os.path.exists(self.database_name):
                os.remove(self.database_name)


    def drop_user(self):
        if 'postgresql' in self.engine:
            subprocess.call([
                'sudo',
                '-u',
                'postgres',
                'dropuser',
                self.database_user
            ])

    def delmigrations(self):
        for migration in glob.glob("**/*/migrations/*.py"):
            if '__init__' not in migration:
                os.remove(migration)

    def handle(self, *args, **options):
        action = options['action']

        if 'create_user' == action:
            self.create_user()
            return

        if 'create' == action:
            self.create()
            return

        if 'drop_user' == action:
            self.drop_user()
            return

        if 'drop' == action:
            self.drop()
            return

        if 'recreate' == action:
            self.drop()
            self.create()
            return

        if 'delmigrations' == action:
            self.delmigrations()
            return
