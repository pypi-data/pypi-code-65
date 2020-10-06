import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('action', nargs='?')

    def install(self):
        subprocess.call(
            ['bower', 'install', '--allow-root' , '--config.interactive=false'], cwd='{0}/website/static'.format(settings.BASE_DIR))

    def handle(self, *args, **options):
        if options['action'] == 'install':
            print("Installing bower dependencies")
            self.install()
        return
