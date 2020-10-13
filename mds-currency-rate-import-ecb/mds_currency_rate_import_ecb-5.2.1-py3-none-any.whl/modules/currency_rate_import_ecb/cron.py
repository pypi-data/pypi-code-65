# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelSingleton, ModelView, ModelSQL, fields, tree
from trytond.pool import Pool, PoolMeta

__all__ = ['Cron']


class Cron(metaclass=PoolMeta):
    "Cron"
    __name__ = "ir.cron"

    @classmethod
    def __setup__(cls):
        super(Cron, cls).__setup__()

        cls.method.selection.append(
            ('currency.currency|cron_update_rate_online', "Currency: Update Exchange Rates"),
            )

# end Cron
