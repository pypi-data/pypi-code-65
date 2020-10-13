# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .configuration import Configuration
from .wizard import UpdateNowWizard
from .currency import Currency


def register():
    Pool.register(
        Configuration,
        Currency,
        module='currency_rate_import_ecb', type_='model')
    Pool.register(
        UpdateNowWizard,
        module='currency_rate_import_ecb', type_='wizard')
