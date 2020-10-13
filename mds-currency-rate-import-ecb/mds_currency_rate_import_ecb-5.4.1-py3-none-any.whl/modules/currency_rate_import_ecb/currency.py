# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelSingleton, ModelView, ModelSQL, fields, tree
from trytond.pool import Pool, PoolMeta

__all__ = ['Currency']


class Currency(metaclass=PoolMeta):
    'Currency'
    __name__ = 'currency.currency'

    currency_update = fields.Boolean(string='Enable online update',
        select = True,
        help="Activates the periodic updating of this currency with data from the ECB.")
    
    # views
    last_update = fields.Function(fields.Date(string='Update', readonly=True),
        'on_change_with_last_update', searcher='search_last_update')

    @classmethod
    def default_currency_update(cls):
        return False

    @fields.depends('rates', 'id')
    def on_change_with_last_update(self, name=None):
        """ get newest rate
        """
        CurrRate = Pool().get('currency.currency.rate')
        
        if isinstance(self.id, type(None)):
            return None

        c_lst = CurrRate.search([
                ('currency', '=', self.id),
            ], order=[('date', 'DESC')], limit=1)
        if len(c_lst) > 0:
            return c_lst[0].date
        return None

    @classmethod
    def search_last_update(cls, name, clause):
        """ search in rates.date
        """
        return [('rates.date',)+clause[1:]]

    @staticmethod
    def order_last_update(tables):
        """ order by date of newest rate
        """
        Config = Pool().get('currency_rate_import_ecb.config')

        tab_cur, _ = tables[None]
        tab_cur_rate = Config.get_currency_rate_sql()

        qu1 = tab_cur_rate.select(tab_cur_rate.date,
                where=(tab_cur_rate.id == tab_cur.id)
            )
        return [qu1]

    @classmethod
    def cron_update_rate_online(cls):
        """ run autoupdate
        """
        Curr1 = Pool().get('currency.currency')

        c_lst = Curr1.search([('currency_update', '=', True)])
        Curr1.update_rate_online(c_lst)

    @classmethod
    def update_rate_online(cls, currencies):
        """ update selected currency
        """
        pool = Pool()
        Config = pool.get('currency_rate_import_ecb.config')

        xml1 = Config.query_rates_ecb()
        r1 = Config.decode_xml(xml1)
        Config.update_rates(currencies, r1)

# end Currency
