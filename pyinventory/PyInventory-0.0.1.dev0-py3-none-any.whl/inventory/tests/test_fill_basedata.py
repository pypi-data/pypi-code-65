from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

# https://github.com/jedie/PyInventory
from inventory.management.commands.fill_basedata import Command as FillBasedataCommand
from inventory.models import DistanceModel


class FillBasedataCommandTestCase(TestCase):
    def test_import_no_username_given(self):
        assert len(settings.BASE_IDEAL_TRACK_LENGTHS) > 0
        assert DistanceModel.objects.count() == 0

        call_command(FillBasedataCommand())

        assert DistanceModel.objects.count() == len(settings.BASE_IDEAL_TRACK_LENGTHS)
