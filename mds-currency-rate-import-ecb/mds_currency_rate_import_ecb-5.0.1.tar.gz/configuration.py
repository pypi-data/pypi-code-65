# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelSingleton, ModelView, ModelSQL, fields, tree
from trytond.pool import Pool
import urllib.request, logging
from trytond.transaction import Transaction
from decimal import Decimal
from datetime import date
import xml.etree.ElementTree as ET


logger = logging.getLogger(__name__)


xmlns = {
    'nsgesmes': 'http://www.gesmes.org/xml/2002-08-01',
    'nsno': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref',
    }

__all__ = ['Configuration']


class Configuration(ModelSingleton, ModelSQL, ModelView):
    'Import Settings'
    __name__ = 'currency_rate_import_ecb.config'

    url = fields.Char(string='Download-URL', required=True,
            help='URL for downloading the XML file from the ECB.')
            
    @classmethod
    def default_url(cls):
        return 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'

    @classmethod
    def query_rates_ecb(cls):
        """ read xml-file from ecb
        """
        Config = Pool().get('currency_rate_import_ecb.config')
        cfg1 = Config.get_singleton()

        # query the ecb
        httpobj = urllib.request.urlopen(cfg1.url, data = None, timeout = 10.0)
        xml1 = httpobj.read()
        httpobj.close()
        del httpobj
        return xml1
        
    @classmethod
    def decode_xml(cls, xmldata):
        """ read xml-file from ceb, decode it
        """
        xmlroot = ET.fromstring(xmldata)
        
        # check incoming data
        # subject
        subj = xmlroot.findall('nsgesmes:subject', xmlns)
        if len(subj) != 1:
            logger.warn('no subject-tag fond in xml-data')
            return None
        if subj[0].text != 'Reference rates':
            logger.warn('invalid subject: %s' % subj[0].text)
            return None
        # sender
        sender = xmlroot.findall('nsgesmes:Sender', xmlns)
        if len(subj) != 1:
            logger.warn('no sender-tag fond in xml-data')
            return None
        sendername = sender[0].findall('nsgesmes:name', xmlns)
        if len(sendername) != 1:
            logger.warn('no name-tag fond in xml-data')
            return None
        if sendername[0].text != 'European Central Bank':
            logger.warn('invalid name: %s' % sendername[0].text)
            return None
        
        # rates
        r1 = {}
        cube1 = xmlroot.findall('nsno:Cube', xmlns)
        if len(cube1) != 1:
            logger.warn('Code-tag (level 0) not found')
            return None
        cube2 = cube1[0].findall('nsno:Cube', xmlns)
        if len(cube2) != 1:
            logger.warn('Code-tag (level 1) not found')
            return None
        
        t1 = cube2[0].attrib['time']
        tl1 = t1.split('-')
        r1['date'] = date(int(tl1[0]), int(tl1[1]), int(tl1[2]))
        cube3 = cube2[0].findall('nsno:Cube', xmlns)
        if len(cube3) == 0:
            logger.warn('Code-tag (level 2) not found')
            return None
        for i in cube3:
            r1[i.attrib['currency']] = Decimal(i.attrib['rate'])
        return r1

    @classmethod
    def get_currency_rate_sql(cls):
        """ get sql for currency + rate, sorted by newest date
        """
        pool = Pool()
        Curr1 = pool.get('currency.currency')
        CurrRate = pool.get('currency.currency.rate')
        tab_cur = Curr1.__table__()
        tab_rate = CurrRate.__table__()

        tab_qu1 = tab_cur.join(tab_rate, 
                condition=tab_cur.id==tab_rate.currency,
                type_ = 'LEFT OUTER',
            ).select(tab_cur.id,
                tab_cur.code,
                tab_rate.date,
                group_by=[tab_cur.id, tab_cur.code, tab_rate.date],
                order_by=[tab_cur.id, tab_rate.date.desc],
                distinct_on=[tab_cur.id]
            )
        return tab_qu1
        
    @classmethod
    def update_rates(cls, currencies, ratesdict):
        """ update rates of currencies
        """
        pool = Pool()
        Curr1 = pool.get('currency.currency')
        CurrRate = pool.get('currency.currency.rate')
        cursor = Transaction().connection.cursor()
        
        # search for currencies, which needs update
        tab_qu1 = cls.get_currency_rate_sql()
        qu2 = tab_qu1.select(tab_qu1.id,
                where=(tab_qu1.id.in_([x.id for x in currencies])) & \
                    (tab_qu1.code.in_(list(ratesdict.keys()))) & \
                    ((tab_qu1.date < ratesdict['date']) | 
                     (tab_qu1.date == None)),
            )
        cursor.execute(*qu2)
        c_lst = cursor.fetchall()

        for i in c_lst:
            cur1 = Curr1(i[0])
            rate1 = CurrRate(
                    date = ratesdict['date'],
                    rate = ratesdict[cur1.code],
                    currency = cur1
                )
            rate1.save()

# end Configuration
