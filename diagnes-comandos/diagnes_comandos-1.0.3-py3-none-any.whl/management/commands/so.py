import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('action', nargs='?')

    def install(self):
        subprocess.call(['sudo', 'apt-get', 'update'])
        for package in open(os.path.join(settings.PROJECT_DIR, 'requirements', 'so.txt')):
            subprocess.call(['sudo', 'apt-get', 'install', package.replace('\n', '')])

    def handle(self, *args, **options):
        if options['action'] == 'install':
            print("Installing OS dependencies")
            self.install()
            return
