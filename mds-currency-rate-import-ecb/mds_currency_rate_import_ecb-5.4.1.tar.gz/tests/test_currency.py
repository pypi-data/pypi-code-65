# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from datetime import date
from decimal import Decimal

xmldata = b"""<?xml version="1.0" encoding="UTF-8"?>
<gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01" xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">
	<gesmes:subject>Reference rates</gesmes:subject>
	<gesmes:Sender>
		<gesmes:name>European Central Bank</gesmes:name>
	</gesmes:Sender>
	<Cube>
		<Cube time="2020-07-23">
			<Cube currency="USD" rate="1.1569"/>
			<Cube currency="JPY" rate="123.98"/>
			<Cube currency="BGN" rate="1.9558"/>
			<Cube currency="CZK" rate="26.342"/>
			<Cube currency="DKK" rate="7.4429"/>
			<Cube currency="GBP" rate="0.91195"/>
			<Cube currency="HUF" rate="347.31"/>
			<Cube currency="PLN" rate="4.4141"/>
			<Cube currency="RON" rate="4.8355"/>
			<Cube currency="SEK" rate="10.2640"/>
			<Cube currency="CHF" rate="1.0731"/>
			<Cube currency="ISK" rate="157.80"/>
			<Cube currency="NOK" rate="10.6073"/>
			<Cube currency="HRK" rate="7.5215"/>
			<Cube currency="RUB" rate="82.5723"/>
			<Cube currency="TRY" rate="7.9229"/>
			<Cube currency="AUD" rate="1.6246"/>
			<Cube currency="BRL" rate="5.9524"/>
			<Cube currency="CAD" rate="1.5486"/>
			<Cube currency="CNY" rate="8.1057"/>
			<Cube currency="HKD" rate="8.9676"/>
			<Cube currency="IDR" rate="16948.00"/>
			<Cube currency="ILS" rate="3.9560"/>
			<Cube currency="INR" rate="86.5770"/>
			<Cube currency="KRW" rate="1389.31"/>
			<Cube currency="MXN" rate="25.9685"/>
			<Cube currency="MYR" rate="4.9267"/>
			<Cube currency="NZD" rate="1.7384"/>
			<Cube currency="PHP" rate="57.202"/>
			<Cube currency="SGD" rate="1.6033"/>
			<Cube currency="THB" rate="36.685"/>
			<Cube currency="ZAR" rate="19.2203"/>
		</Cube>
	</Cube>
</gesmes:Envelope>"""

class CurrencyTestCase(ModuleTestCase):
    'Test currency rate module'
    module = 'currency_rate_import_ecb'

    def prep_currency_config(self):
        """ create config
        """
        Config = Pool().get('currency_rate_import_ecb.config')
        
        cfg1 = Config()
        cfg1.save()
        
        cfg2 = Config.get_singleton()
        self.assertEqual(cfg2.url, 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml')
        return cfg2
        
    @with_transaction()
    def test_currency_config(self):
        """ create config
        """
        self.prep_currency_config()
    
    @with_transaction()
    def test_currency_read_ecb_xml(self):
        """ read xml-file from ecb
        """
        Config = Pool().get('currency_rate_import_ecb.config')
        
        self.prep_currency_config()
        
        #xml1 = Config.query_rates_ecb()
        #self.assertTrue(isinstance(xml1, type(b'')))

    @with_transaction()
    def test_currency_decode_xml(self):
        """ decode a file from ecb
        """
        Config = Pool().get('currency_rate_import_ecb.config')
        
        r1 = Config.decode_xml(xmldata)
        self.assertEqual(r1['date'], date(2020, 7, 23))
        self.assertEqual(str(r1['USD']), '1.1569')
        self.assertEqual(str(r1['JPY']), '123.98')
        self.assertEqual(str(r1['BGN']), '1.9558')
        self.assertEqual(str(r1['CZK']), '26.342')
    
    @with_transaction()
    def test_currency_create_item_with_former_rate(self):
        """ add currency + rate, check field + search
        """
        pool = Pool()
        Curreny = pool.get('currency.currency')
        CurrRate = pool.get('currency.currency.rate')
        
        c1 = Curreny(
                name = 'EURO',
                symbol = 'e',
                code = 'EUR',
                numeric_code = '123',
                rates = [
                    CurrRate(
                        date = date(2020, 7, 15),
                        rate = Decimal('1.5'),
                        ),
                    CurrRate(
                        date = date(2020, 7, 16),
                        rate = Decimal('1.51'),
                        ),
                    ],
            )
        c1.save()
        
        cl1 = Curreny.search([])
        self.assertEqual(len(cl1), 1)
        self.assertEqual(cl1[0].name, 'EURO')
        self.assertEqual(cl1[0].symbol, 'e')
        self.assertEqual(len(cl1[0].rates), 2)
        self.assertEqual(str(cl1[0].rates[0].date), '2020-07-16')
        self.assertEqual(str(cl1[0].rates[0].rate), '1.51')
        self.assertEqual(str(cl1[0].rates[1].date), '2020-07-15')
        self.assertEqual(str(cl1[0].rates[1].rate), '1.5')
        self.assertEqual(str(cl1[0].rate), '1.51')
        
        # search
        cl2 = Curreny.search([('last_update', '=', date(2020, 7, 16))])
        self.assertEqual(len(cl2), 1)
        cl2 = Curreny.search([('last_update', '<', date(2020, 7, 15))])
        self.assertEqual(len(cl2), 0)
        cl2 = Curreny.search([('last_update', 'in', [date(2020, 7, 15)])])
        self.assertEqual(len(cl2), 1)

    @with_transaction()
    def test_currency_create_item(self):
        """ add currency + rate, check field + search
        """
        pool = Pool()
        Curreny = pool.get('currency.currency')
        CurrRate = pool.get('currency.currency.rate')
        
        c1 = Curreny(
                name = 'EURO',
                symbol = 'e',
                code = 'EUR',
                numeric_code = '123',
                rates = [
                    CurrRate(
                        date = date(2020, 7, 15),
                        rate = Decimal('1.5'),
                        ),
                    CurrRate(
                        date = date(2020, 7, 16),
                        rate = Decimal('1.51'),
                        ),
                    ],
            )
        c1.save()
        
        cl1 = Curreny.search([])
        self.assertEqual(len(cl1), 1)
        self.assertEqual(cl1[0].name, 'EURO')
        self.assertEqual(cl1[0].symbol, 'e')
        self.assertEqual(len(cl1[0].rates), 2)
        self.assertEqual(str(cl1[0].rates[0].date), '2020-07-16')
        self.assertEqual(str(cl1[0].rates[0].rate), '1.51')
        self.assertEqual(str(cl1[0].rates[1].date), '2020-07-15')
        self.assertEqual(str(cl1[0].rates[1].rate), '1.5')
        self.assertEqual(str(cl1[0].rate), '1.51')
        
        # search
        cl2 = Curreny.search([('last_update', '=', date(2020, 7, 16))])
        self.assertEqual(len(cl2), 1)
        cl2 = Curreny.search([('last_update', '<', date(2020, 7, 15))])
        self.assertEqual(len(cl2), 0)
        cl2 = Curreny.search([('last_update', 'in', [date(2020, 7, 15)])])
        self.assertEqual(len(cl2), 1)

    @with_transaction()
    def test_currency_update_item_by_ebc_data_former_rate(self):
        """ add currency + rate, update rate by xml-data
        """
        pool = Pool()
        Curreny = pool.get('currency.currency')
        CurrRate = pool.get('currency.currency.rate')
        Config = pool.get('currency_rate_import_ecb.config')
        
        c1 = Curreny(
                name = 'USD',
                symbol = 's',
                code = 'USD',
                numeric_code = '123',
                rates = [
                    CurrRate(
                        date = date(2020, 7, 15),
                        rate = Decimal('1.5'),
                        ),
                    CurrRate(
                        date = date(2020, 7, 16),
                        rate = Decimal('1.51'),
                        ),
                    ],
            )
        c1.save()
        cl1 = Curreny.search([])
        self.assertEqual(len(cl1), 1)
        self.assertEqual(cl1[0].name, 'USD')
        self.assertEqual(cl1[0].symbol, 's')
        self.assertEqual(len(cl1[0].rates), 2)
        self.assertEqual(str(cl1[0].rates[0].date), '2020-07-16')
        self.assertEqual(str(cl1[0].rates[0].rate), '1.51')
        self.assertEqual(str(cl1[0].rates[1].date), '2020-07-15')
        self.assertEqual(str(cl1[0].rates[1].rate), '1.5')
        self.assertEqual(str(cl1[0].rate), '1.51')
        
        r1 = Config.decode_xml(xmldata)
        Config.update_rates([c1], r1)

        cl1 = Curreny.search([])
        self.assertEqual(len(cl1), 1)
        self.assertEqual(cl1[0].name, 'USD')
        self.assertEqual(cl1[0].symbol, 's')
        self.assertEqual(len(cl1[0].rates), 3)
        self.assertEqual(str(cl1[0].rates[0].date), '2020-07-23')
        self.assertEqual(str(cl1[0].rates[0].rate), '1.1569')
        self.assertEqual(str(cl1[0].rates[1].date), '2020-07-16')
        self.assertEqual(str(cl1[0].rates[1].rate), '1.51')
        self.assertEqual(str(cl1[0].rates[2].date), '2020-07-15')
        self.assertEqual(str(cl1[0].rates[2].rate), '1.5')
        self.assertEqual(str(cl1[0].rate), '1.1569')

    @with_transaction()
    def test_currency_update_item_by_ebc_data_no_rate(self):
        """ add currency, update rate by xml-data
        """
        pool = Pool()
        Curreny = pool.get('currency.currency')
        CurrRate = pool.get('currency.currency.rate')
        Config = pool.get('currency_rate_import_ecb.config')
        
        c1 = Curreny(
                name = 'USD',
                symbol = 's',
                code = 'USD',
                numeric_code = '123',
            )
        c1.save()
        cl1 = Curreny.search([])
        self.assertEqual(len(cl1), 1)
        self.assertEqual(cl1[0].name, 'USD')
        self.assertEqual(cl1[0].symbol, 's')
        self.assertEqual(len(cl1[0].rates), 0)
        self.assertEqual(str(cl1[0].rate), '0')
        
        # no rates exists,  add one
        r1 = Config.decode_xml(xmldata)
        Config.update_rates([c1], r1)

        cl1 = Curreny.search([])
        self.assertEqual(len(cl1), 1)
        self.assertEqual(cl1[0].name, 'USD')
        self.assertEqual(cl1[0].symbol, 's')
        self.assertEqual(len(cl1[0].rates), 1)
        self.assertEqual(str(cl1[0].rates[0].date), '2020-07-23')
        self.assertEqual(str(cl1[0].rates[0].rate), '1.1569')
        self.assertEqual(str(cl1[0].rate), '1.1569')

    @with_transaction()
    def test_currency_update_item_by_ebc_data_current_rate(self):
        """ add currency + rate, update rate by xml-data, rate of current day exists
        """
        pool = Pool()
        Curreny = pool.get('currency.currency')
        CurrRate = pool.get('currency.currency.rate')
        Config = pool.get('currency_rate_import_ecb.config')
        
        c1 = Curreny(
                name = 'USD',
                symbol = 's',
                code = 'USD',
                numeric_code = '123',
                rates = [
                    CurrRate(
                        date = date(2020, 7, 23),
                        rate = Decimal('1.5'),
                        ),
                    CurrRate(
                        date = date(2020, 7, 16),
                        rate = Decimal('1.51'),
                        ),
                    ],
            )
        c1.save()
        cl1 = Curreny.search([])
        self.assertEqual(len(cl1), 1)
        self.assertEqual(cl1[0].name, 'USD')
        self.assertEqual(cl1[0].symbol, 's')
        self.assertEqual(len(cl1[0].rates), 2)
        self.assertEqual(str(cl1[0].rates[0].date), '2020-07-23')
        self.assertEqual(str(cl1[0].rates[0].rate), '1.5')
        self.assertEqual(str(cl1[0].rates[1].date), '2020-07-16')
        self.assertEqual(str(cl1[0].rates[1].rate), '1.51')
        self.assertEqual(str(cl1[0].rate), '1.5')
        
        # rate for current day exists, dont try to add another one
        r1 = Config.decode_xml(xmldata)
        Config.update_rates([c1], r1)

        cl1 = Curreny.search([])
        self.assertEqual(len(cl1), 1)
        self.assertEqual(cl1[0].name, 'USD')
        self.assertEqual(cl1[0].symbol, 's')
        self.assertEqual(len(cl1[0].rates), 2)
        self.assertEqual(str(cl1[0].rates[0].date), '2020-07-23')
        self.assertEqual(str(cl1[0].rates[0].rate), '1.5')
        self.assertEqual(str(cl1[0].rates[1].date), '2020-07-16')
        self.assertEqual(str(cl1[0].rates[1].rate), '1.51')
        self.assertEqual(str(cl1[0].rate), '1.5')

# end CurrencyTestCase
