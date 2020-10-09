from django.core.management.base import BaseCommand

from ...utils.couchdb import dumpdata


class Command(BaseCommand):
    help = 'Performs complete dumpdata to couchdb instance.'

    def handle(self, *args, **options):
        try:
           dumpdata()

        except Exception as e:
            self.stdout.write(self.style.ERROR('Error "{}"'.format(e)))

        else:
            self.stdout.write(self.style.SUCCESS('Done'))
