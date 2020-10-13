# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import trytond.tests.test_tryton
import unittest

from trytond.modules.currency_rate_import_ecb.tests.test_currency import CurrencyTestCase

__all__ = ['suite']


class CurrencyRateModuleTestCase(\
            CurrencyTestCase):
    'Test currency rate module'
    module = 'currency_rate_import_ecb'

#end CurrencyRateModuleTestCase


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(CurrencyRateModuleTestCase))
    return suite
