"""
    created 30.05.2018 by Jens Diemer <opensource@jensdiemer.de>
    :copyleft: 2018 by the PyInventory team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import logging

from django.contrib import admin

# https://github.com/jedie/PyInventory
from inventory.models import DisciplineModel


log = logging.getLogger(__name__)


@admin.register(DisciplineModel)
class DisciplineModelAdmin(admin.ModelAdmin):
    pass
