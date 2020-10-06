import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('action', nargs='?')

    def install(self):
        for package in open(os.path.join(settings.PROJECT_DIR, 'requirements', 'npm.txt')):
            subprocess.call(
                ['sudo', 'npm', 'install', '-g', package])

    def handle(self, *args, **options):
        if options['action'] == 'install':
            print("Installing NPM dependencies")
            self.install()
            return
