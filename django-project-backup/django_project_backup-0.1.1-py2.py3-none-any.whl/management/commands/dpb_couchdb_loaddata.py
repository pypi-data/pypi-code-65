from django.core.management.base import BaseCommand

from ...utils.couchdb import loaddata


class Command(BaseCommand):
    help = 'Performs complete loaddata from couchdb instance.'

    def handle(self, *args, **options):
        try:
           loaddata()

        except Exception as e:
            self.stdout.write(self.style.ERROR('Error "{}"'.format(e)))

        else:
            self.stdout.write(self.style.SUCCESS('Done'))
