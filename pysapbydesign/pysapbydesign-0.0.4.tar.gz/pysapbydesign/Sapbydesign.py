import datetime

import pandas as pd
import requests
import yaml
from dacktool import log_info, log_error
from requests.auth import HTTPBasicAuth

from pysapbydesign.auth import get_credentials_and_tenant_hostname
import xml.etree.ElementTree as ET


def treat_result(list_dict):
    all_c = []
    for el in list_dict:
        all_c = all_c + list(el.keys())
    all_c = list(set(all_c))
    return [c.replace('-', '_').lower() for c in all_c], [{c.replace('-', '_').lower(): el.get(c) for c in all_c} for el
                                                          in list_dict]


def process_metadata(content):
    root = ET.fromstring(content)
    replace = {
        'edmx': "http://schemas.microsoft.com/ado/2007/06/edmx",
        'xmlns': "http://schemas.microsoft.com/ado/2008/09/edm"
    }
    result = []
    for properties_el in root.findall(
            "./{%(edmx)s}DataServices/{%(xmlns)s}Schema/{%(xmlns)s}EntityType/{%(xmlns)s}Property" % replace):
        attrib = properties_el.attrib
        attrib = {i.replace('{http://www.sap.com/Protocols/SAPData}', ''): attrib[i] for i in attrib}
        result.append(attrib)
    all_columns, result = treat_result(result)
    return all_columns, result


def process_el(el):
    for d in el:
        if '/Date' in str(el[d]):
            temp = el[d].replace('/Date(', '').replace(')/', '')
            el[d] = str(datetime.datetime.fromtimestamp(int(temp[:-3])))[:10]
    return el


def process_date(elem):
    temp = elem.replace('/Date(', '').replace(')/', '')
    return str(datetime.datetime.fromtimestamp(int(temp[:-3])))[:10]


def process_data(input_data):
    i = 0
    all_columns = []
    new_input_data = []
    for ela in input_data:
        print(i)
        ela['PARA_FISCYEARPER'] = int(ela.get('CFISCYEAR') + (ela.get('CFISCPER') if len(
            ela.get('CFISCPER')) == 2 else '0' + ela.get('CFISCPER')))
        new_input_data.append(ela)
        i = i + 1
    for elb in new_input_data:
        print(i)
        i = i + 1
        all_columns = all_columns + list(elb.keys())
    all_columns = list(set(all_columns))
    all_columns.remove('__metadata')
    result = [{c.lower(): process_el(elc).get(c) for c in all_columns} for elc in new_input_data]
    all_columns = [c.lower() for c in all_columns]
    return all_columns, result


def process_df(input_data):
    input_data = input_data.drop(columns=['__metadata'])
    input_data['CPOSTING_DATE'] = input_data['CPOSTING_DATE'].apply(process_date)
    input_data['PARA_FISCYEARPER'] = input_data['CFISCYEAR'] + input_data['CFISCPER'].apply(
        lambda x: x if len(x) == 2 else '0' + x)
    return list(input_data.columns), list(list(r) for r in input_data.values)


def from_sap_format_to_db(date):
    sap_date = str(date)
    if len(sap_date) == 5:
        return int(sap_date[1:] + '0' + sap_date[0])
    return int(sap_date[2:] + sap_date[:2])


def get_sap_date_filter(_object, start, end):
    date_field = _object.get('date_field')
    if not end:
        return ["(" + date_field + " ge " + str(start) + ")"]
    if not start:
        return ["(" + date_field + " le " + str(end) + ")"]
    return ["(" + date_field + " ge " + str(start) + " and " + date_field + " le " + str(end) + ")"]


class Sapbydesign:

    def __init__(self, var_env_key, dbstream, config_file_path):
        self.var_env_key = var_env_key
        self.dbstream = dbstream
        self.config_file_path = config_file_path

        self.credentials, self.tenant_hostname = get_credentials_and_tenant_hostname(var_env_key)
        self.objects = yaml.load(open(self.config_file_path), Loader=yaml.FullLoader).get('objects')
        self.schema_prefix = yaml.load(open(self.config_file_path), Loader=yaml.FullLoader).get("schema_prefix")

    def _get(self, url, params=None, headers=None):
        result = requests.get(url,
                              auth=HTTPBasicAuth(self.credentials.get('User'), self.credentials.get('Password')),
                              headers=headers, params=params)
        return result

    def _get_date_report(self, _object):
        date_field = _object.get('date_field').lower()
        table_name = "%s.%s" % (self.schema_prefix, _object.get('table'))
        query = "SELECT max(%s) as max_date FROM %s" % (date_field, table_name)
        start = str(self.dbstream.execute_query(query)[0]['max_date'])
        start_year = start[:4]
        start_month = start[4:] if start[4] != 0 else start[5:]
        return start_month + start_year

    def get_report(self, _object_key, sap_para_fiscyearper_start=None,
                   sap_para_fiscyearper_end=None, cleaning=True):
        _object = self.objects[_object_key]
        for ccomp in _object.get('filter').get('PARA_COMPANY'):
            para_company = ccomp
            for setofbks in _object.get('filter').get('PARA_COMPANY').get(ccomp).get('PARA_SETOFBKS'):
                para_setofbks = setofbks
                log_info('PARA_COMPANY: %s - PARA_SETOFBKS: %s' % (para_company, setofbks))
                self._get_specific_report(_object_key, para_setofbks, para_company, sap_para_fiscyearper_start,
                                          sap_para_fiscyearper_end, cleaning)

    def _get_specific_report(self, _object_key, para_setofbks, para_company, sap_para_fiscyearper_start=None,
                             sap_para_fiscyearper_end=None, cleaning=True):
        _object = self.objects[_object_key]
        query_filter = ["PARA_SETOFBKS eq '%s'" % para_setofbks, "PARA_COMPANY eq '%s'" % para_company]
        if not sap_para_fiscyearper_start and not sap_para_fiscyearper_end:
            sap_para_fiscyearper_start = self._get_date_report(_object)
        sap_date_filter = get_sap_date_filter(_object, sap_para_fiscyearper_start, sap_para_fiscyearper_end)
        params = {
            '$inlinecount': _object.get('inlinecount'),
            '$select': ','.join(_object.get('select')),
            '$filter': ' and '.join(query_filter + sap_date_filter),
            '$top': _object.get('top'),
            '$skip': _object.get('skip'),
            '$format': _object.get('format')
        }
        headers = {
            'Accept': 'application/json',
            'Content-type': 'application/json'
        }

        url = "https://%(tenant_hostname)s" \
              "sap/byd/odata/fin_generalledger_analytics.svc/" \
              "RP%(report_id)sQueryResults" % {'tenant_hostname': self.tenant_hostname,
                                               'report_id': _object.get('report_id')}
        total_result = []
        result = self._get(url, params, headers).json()
        try:
            total_result = total_result + result['d'].get('results')
        except KeyError:
            log_error(result)
            return total_result
        count = int(result['d'].get('__count'))
        total_result_fetch = len(result['d'].get('results'))
        log_info('Result fetched: %s/%s' % (str(total_result_fetch), str(count)))
        while total_result_fetch < count and _object.get('paging') is not False:
            params['$skip'] = total_result_fetch
            result = self._get(url, params, headers).json()
            total_result_fetch = total_result_fetch + len(result['d'].get('results'))
            total_result = total_result + result['d'].get('results')
            log_info('Result fetched: %s/%s' % (str(total_result_fetch), str(count)))
        if count == 0:
            log_info('No result')
            return total_result
        total_result = pd.DataFrame(total_result)
        total_result.to_pickle('sandbox_result')
        all_columns, total_result = process_df(total_result)
        updated_at = datetime.datetime.now()
        table_name = "%s.%s" % (self.schema_prefix, _object.get('table'))
        data = {
            "table_name": table_name,
            "columns_name": all_columns + ['para_setofbks', 'updated_at'],
            "rows": [r + [para_setofbks, updated_at] for r in total_result]
        }
        date_field = _object.get('date_field').lower()
        if cleaning:
            if sap_para_fiscyearper_start and not sap_para_fiscyearper_end:
                cleaning_query = 'DELETE FROM %s WHERE %s >= %s ' % (
                    table_name, date_field, from_sap_format_to_db(sap_para_fiscyearper_start))
            elif sap_para_fiscyearper_end and not sap_para_fiscyearper_start:
                cleaning_query = 'DELETE FROM %s WHERE %s <= %s ' % (
                    table_name, date_field, from_sap_format_to_db(sap_para_fiscyearper_end))
            else:
                cleaning_query = 'DELETE FROM %s WHERE %s >= %s  and %s <= %s' % (
                    table_name, date_field, from_sap_format_to_db(sap_para_fiscyearper_start), date_field,
                    from_sap_format_to_db(sap_para_fiscyearper_end))
            cleaning_query = cleaning_query + " and para_setofbks='%s' and ccompany_uuid='%s'" % (
                para_setofbks, para_company)
            log_info('Cleaning: ' + cleaning_query)
            self.dbstream.execute_query(cleaning_query)
        self.dbstream.send_data(data, replace=False)
        return total_result

    def get_metadata(self, _object_key):
        _object = self.objects[_object_key]
        url = "https://%(tenant_hostname)s" \
              "sap/byd/odata/fin_generalledger_analytics.svc/$metadata?" \
              "entityset=RP%(report_id)sQueryResults&sap-label=true&sap-language=fr&=" % {
                  'tenant_hostname': self.tenant_hostname, 'report_id': _object.get('report_id')}
        all_columns, metadata = process_metadata(self._get(url).content)
        data = {
            "table_name": "%s.%s_metadata" % (self.schema_prefix, _object.get('table')),
            "columns_name": all_columns,
            "rows": [[r[i] for i in all_columns] for r in metadata]
        }
        self.dbstream.send_data(data, replace=True)
