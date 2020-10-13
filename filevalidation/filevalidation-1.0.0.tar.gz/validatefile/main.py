__Author__ = "Ram Prakash Jayapalan"
__PyVersion__ = 3


import configparser
import os
import re
import csv
from multiprocessing import Pool, Manager, Process
from validatefile import helper
import random
from datetime import datetime
from functools import partial
import logging
import time

logging.basicConfig(level='INFO',
                    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
log = logging.getLogger('ValidateFile')


class SectionMissingError(Exception):
    pass


class ValidateFile(object):
    """
    File validation class
    """
    __slots__ = ('_configfile', '_sourcefile', '_dictconfig', '_outputqueue')

    def __init__(self, configfile: str, sourcefile: str) -> None:
        self._configfile = configfile
        self._sourcefile = sourcefile
        self._dictconfig = None
        self._outputqueue = Manager().Queue()
        # Set config file as dict object
        self._set_dictconfig()

    def _set_dictconfig(self) -> None:
        """
        Setter method to parse config info from config file
        """
        config = configparser.ConfigParser(allow_no_value=True)
        config.optionxform = str
        config.read(self._configfile)
        sections = config.sections()
        dictconfig = dict()
        if 'global.settings' not in sections:
            raise SectionMissingError('global.settings sections missing')
        if 'Delimiter' not in config['global.settings']:
            raise KeyError('Delimiter key/value missing under'
                           ' global.settings section')
        if 'Encoding' not in config['global.settings']:
            raise KeyError('Encoding key/value missing under'
                           ' global.settings section')
        dictconfig['Delimiter'] = config['global.settings']['Delimiter']
        dictconfig['Encoding'] = config['global.settings']['Encoding']
        dictconfig['Filename'] = config.get('file.rules', 'Filename',
                                            fallback=None)
        dictconfig['FilenameError'] = config.get('file.rules',
                                                 'FilenameErrorMessage',
                                                 fallback='Filename validation'
                                                 ' failed')
        dictconfig['ValidateHeader'] = config.getboolean('header.rules',
                                                         'ValidateHeader',
                                                         fallback=False)
        dictconfig['HCaseSensitive'] = config.getboolean('header.rules',
                                                         'CaseSensitive',
                                                         fallback=False)
        fb = 'Could not find a match for the header "{headername}"'
        dictconfig['HeaderError'] = config.get('header.rules',
                                               'HeaderErrorMessage',
                                               fallback=fb)
        dictconfig['MatchHeaderCount'] = config.getboolean('header.rules',
                                                           'MatchHeaderCount',
                                                           fallback=False)
        fb = 'Header count does not match (required : {requiredcount} | '\
            'available : {availablecount})'
        dictconfig['HeaderCountError'] = config.get('header.rules',
                                                    'HeaderCountErrorMessage',
                                                    fallback=fb)
        dictconfig['Header'] = [h for h in config['header']]
        dictconfig['ValidateColumn'] = config.getboolean('column.rules',
                                                         'ValidateColumn',
                                                         fallback=False)
        dictconfig['EmptyCheck'] = {c for c in config['EmptyCheck']}
        dictconfig['_EmptyCheck'] = {c.lower() for c in
                                     dictconfig['EmptyCheck']} \
            if not dictconfig['HCaseSensitive'] else dictconfig['EmptyCheck']
        fb = '"{fieldname}" failed empty check'
        dictconfig['EmptyCheckDesc'] = config.get('EmptyCheck.description',
                                                  'Description', fallback=fb)
        dictconfig['NumericCheck'] = {c for c in config['NumericCheck']}
        dictconfig['_NumericCheck'] = {c.lower() for c in
                                       dictconfig['NumericCheck']} \
            if not dictconfig['HCaseSensitive'] else dictconfig['NumericCheck']
        fb = '"{fieldname}" failed numeric check'
        dictconfig['NumericCheckDesc'] = config.get('NumericCheck.description',
                                                    'Description', fallback=fb)
        dictconfig['IntegerCheck'] = {c for c in config['IntegerCheck']}
        dictconfig['_IntegerCheck'] = {c.lower() for c in
                                       dictconfig['IntegerCheck']} \
            if not dictconfig['HCaseSensitive'] else dictconfig['IntegerCheck']
        fb = '"{fieldname}" failed integer check'
        dictconfig['IntegerCheckDesc'] = config.get('IntegerCheck.description',
                                                    'Description', fallback=fb)
        dictconfig['DecimalCheck'] = {c for c in config['DecimalCheck']}
        dictconfig['_DecimalCheck'] = {c.lower() for c in
                                       dictconfig['DecimalCheck']} \
            if not dictconfig['HCaseSensitive'] else dictconfig['DecimalCheck']
        fb = '"{fieldname}" failed decimal check'
        dictconfig['DecimalCheckDesc'] = config.get('DecimalCheck.description',
                                                    'Description',
                                                    fallback=fb)
        dictconfig['FormatCheck'] = [{c: eval(config.get('FormatCheck', c))}
                                     for c in config['FormatCheck']]
        val = dict()
        for idx, item in enumerate(dictconfig['FormatCheck']):
            for k, v in item.items():
                if not dictconfig['HCaseSensitive']:
                    val[k.lower()] = idx
                else:
                    val[k] = idx
        dictconfig['_FormatCheck'] = val
        fb = '"{fieldname}" failed format check'
        dictconfig['FormatCheckDesc'] = config.get('FormatCheck.description',
                                                   'Description',
                                                   fallback=fb)
        dictconfig['LengthCheck'] = [{c: eval(config.get('LengthCheck', c))}
                                     for c in config['LengthCheck']]
        val = dict()
        for idx, item in enumerate(dictconfig['LengthCheck']):
            for k, v in item.items():
                if not dictconfig['HCaseSensitive']:
                    val[k.lower()] = idx
                else:
                    val[k] = idx
        dictconfig['_LengthCheck'] = val
        fb = '"{fieldname}" failed length check'
        dictconfig['LengthCheckDesc'] = config.get('LengthCheck.description',
                                                   'Description',
                                                   fallback=fb)
        self._dictconfig = dictconfig

    @property
    def dictconfig(self):
        return self._dictconfig

    @property
    def configfile(self):
        return self._configfile

    @property
    def sourcefile(self):
        return self._sourcefile

    def _validatefilename(self, value: str) -> dict:
        """
        Method to validate filename
        :param value: Filename of the source file
        """
        expectedpattern = self._dictconfig['Filename']
        if not re.fullmatch(pattern=expectedpattern, string=value):
            return {'Level': 'Filename',
                    'Error': self._dictconfig['FilenameError']}
        else:
            return {}

    def _validateheader(self, value: list) -> dict:
        """
        Method to validate header
        :param value: header to be validated
        """
        missingheader = list()
        availableheader = value
        givenheader = self._dictconfig['Header']
        _givenheader = givenheader[:]
        if self._dictconfig['HCaseSensitive'] is False:
            availableheader = [h.lower() for h in availableheader]
            givenheader = [h.lower() for h in givenheader]
        for i, e in enumerate(givenheader):
            if e not in availableheader:
                missingheader.append(self._dictconfig['HeaderError']
                                     .format(headername=_givenheader[i]))
        if missingheader:
            return {'Level': 'Header', 'Error': missingheader}
        else:
            return {}

    def _validateheadercount(self, value: list) -> dict:
        """
        Method to validate header count
        :param value: header to be validated
        """
        requiredcount = len(self._dictconfig['Header'])
        availablecount = 0
        availableheader = value
        availablecount = len(availableheader)
        if requiredcount != availablecount:
            err = self._dictconfig['HeaderCountError']\
                  .format(requiredcount=requiredcount,
                          availablecount=availablecount)
            return {'Level': 'HeaderCount', 'Error': err}
        else:
            return {}

    def _validaterecord(self, value: dict) -> dict:
        """
        Method to validate given record
        :param value: dict containing header and row as key/value
        """
        # For every field in a given record, perform validation based on the
        # config file
        error_desc = list()
        error_count = dict()
        for k, v in value.items():
            # Empty check
            if (k in self._dictconfig['_EmptyCheck'] or
               k.lower() in self._dictconfig['_EmptyCheck']):
                if helper.isempty(value=v):
                    error_desc.append(self._dictconfig['EmptyCheckDesc']
                                      .format(fieldname=k))
                    error_count['EmptyCheck'] = error_count\
                        .setdefault('EmptyCheck', 0) + 1
            # Numeric check
            if (k in self._dictconfig['_NumericCheck'] or
               k.lower() in self._dictconfig['_NumericCheck']) and \
               helper.isempty(value=v) is False:
                if not helper.isnumeric(value=v):
                    error_desc.append(self._dictconfig['NumericCheckDesc']
                                      .format(fieldname=k))
                    error_count['NumericCheck'] = error_count\
                        .setdefault('NumericCheck', 0) + 1
            # Integer check
            if (k in self._dictconfig['_IntegerCheck'] or
               k.lower() in self._dictconfig['_IntegerCheck']) and \
               helper.isempty(value=v) is False:
                if not helper.isinteger(value=v):
                    error_desc.append(self._dictconfig['IntegerCheckDesc']
                                      .format(fieldname=k))
                    error_count['IntegerCheck'] = error_count\
                        .setdefault('IntegerCheck', 0) + 1
            # Decimal check
            if (k in self._dictconfig['_DecimalCheck'] or
               k.lower() in self._dictconfig['_DecimalCheck']) and \
               helper.isempty(value=v) is False:
                if not helper.isdecimal(value=v):
                    error_desc.append(self._dictconfig['DecimalCheckDesc']
                                      .format(fieldname=k))
                    error_count['DecimalCheck'] = error_count\
                        .setdefault('DecimalCheck', 0) + 1
            # Format check
            if (k in self._dictconfig['_FormatCheck'] or
               k.lower() in self._dictconfig['_FormatCheck']) and \
               helper.isempty(value=v) is False:
                try:
                    pos = self._dictconfig['_FormatCheck'][k]
                except KeyError:
                    pos = self._dictconfig['_FormatCheck'][k.lower()]
                key = [_ for _ in self._dictconfig['FormatCheck'][pos]
                       .keys()][0]
                d = self._dictconfig['FormatCheck'][pos][key]
                pattern = d['pattern']
                count = d.get('count', None)
                ignorecase = d.get('ignorecase', False)
                if not helper.isexpectedformat(string=v, pattern=pattern,
                                               count=count,
                                               ignorecase=ignorecase):
                    error_desc.append(self._dictconfig['FormatCheckDesc']
                                      .format(fieldname=k))
                    error_count['FormatCheck'] = error_count\
                        .setdefault('FormatCheck', 0) + 1
            # Length check
            if (k in self._dictconfig['_LengthCheck'] or
               k.lower() in self._dictconfig['_LengthCheck']) and \
               helper.isempty(value=v) is False:
                try:
                    pos = self._dictconfig['_LengthCheck'][k]
                except KeyError:
                    pos = self._dictconfig['_LengthCheck'][k.lower()]
                key = [_ for _ in self._dictconfig['LengthCheck'][pos]
                       .keys()][0]
                d = self._dictconfig['LengthCheck'][pos][key]
                maxvalue = d['max']
                minvalue = d.get('min', None)
                if not helper.isexpectedlength(value=v, maxvalue=maxvalue,
                                               minvalue=minvalue):
                    error_desc.append(self._dictconfig['LengthCheckDesc']
                                      .format(fieldname=k))
                    error_count['LengthCheck'] = error_count\
                        .setdefault('LengthCheck', 0) + 1
        if error_desc:
            return {'Level': 'Field', 'Error': error_desc,
                    'ErrorCount': error_count}
        else:
            return {}

    def _process(self, writeout: bool, value: dict) -> dict:
        """
        Method to orchestrate field validations.
        :param value: dict containing header and row as key/value
        :param writeout: set to True if the results need to be written to
        outout file.
        """
        ret = self._validaterecord(value=value)
        if ret:
            value['_is_error'] = 1
            value['_error_desc'] = '; '.join(ret['Error'])
        else:
            value['_is_error'] = 0
            value['_error_desc'] = None
        if writeout:
            self._outputqueue.put(value)
        return ret

    def _writeout(self, fieldnames: list, outputfile: str) -> None:
        """
        Method to write validation results as output
        """
        with open(file=outputfile, mode='w+', encoding='utf-8') as fo:
            writer = csv.DictWriter(f=fo, fieldnames=fieldnames,
                                    delimiter='\t')
            writer.writeheader()
            while True:
                item = self._outputqueue.get(timeout=10)
                if item is None:
                    break
                log.debug(item)
                writer.writerow(rowdict=item)
        self._outputqueue.task_done()

    def getresult(self, outputdir: str = None) -> dict:
        """
        Method to invoke validation process
        Specifying output dir will write all the field level errors along
        with original records in txt tab delimited format.
        There will be 2 additional columns `_is_error` and `_error_desc`
        for error flag and error description respectively
        """
        log.info('Starting file validation process')
        starttime = time.time()
        fo = None
        prc = None
        errcount = dict()
        writeout = False
        if outputdir:
            if not os.path.isdir(outputdir):
                raise NotADirectoryError('The given path is not a valid'
                                         ' dir path')
            outfilename = ''.join([random.choice('abcdefghij')
                                   for _ in range(8)] +
                                  [datetime.now().strftime('_%Y%m%d%M%S.txt')])
            outputfile = os.path.join(outputdir, outfilename)
            writeout = True
        result = {
            'Results': {
                'TotalRecordsAnalysed': 0,
                'RecordsPassed': 0,
                'RecordsFailed': 0,
                'ErrorDetails': [],
                'OutputFile': None
            }
        }
        try:
            if self._dictconfig['Filename']:
                log.info('Validating filename')
                filename = os.path.basename(self._sourcefile)
                val = self._validatefilename(value=filename)
                if val:
                    result['Results']['ErrorDetails'].append(val)
            if not self._dictconfig['ValidateHeader'] and \
               not self._dictconfig['MatchHeaderCount'] and \
               not self._dictconfig['ValidateColumn']:
                return result
            fo = open(file=self._sourcefile, mode='r',
                      encoding=self._dictconfig['Encoding'])
            reader = csv.DictReader(f=fo,
                                    delimiter=self._dictconfig['Delimiter']
                                    .encode().decode('unicode_escape'))
            fieldnames = reader.fieldnames
            if self._dictconfig['ValidateHeader']:
                log.info('Validating header')
                val = self._validateheader(value=fieldnames)
                if val:
                    result['Results']['ErrorDetails'].append(val)
            if self._dictconfig['MatchHeaderCount']:
                log.info('Validating header count')
                val = self._validateheadercount(value=fieldnames)
                if val:
                    result['Results']['ErrorDetails'].append(val)
            if self._dictconfig['ValidateColumn']:
                log.info('Validating fields')
                # Start the consumer process in a thread to write output only
                # if outuput dir is available.
                if writeout:
                    fieldnames.extend(['_is_error', '_error_desc'])
                    prc = Process(target=self._writeout,
                                  args=(fieldnames, outputfile), daemon=True)
                    prc.start()
                # Process record validation by assigning records
                # to pool of workers
                pool = Pool().imap(func=partial(self._process, writeout),
                                   iterable=reader, chunksize=25000)
                for d in pool:
                    result['Results']['TotalRecordsAnalysed'] += 1
                    if d:
                        result['Results']['RecordsFailed'] += 1
                        for k, v in d['ErrorCount'].items():
                            errcount[k] = errcount.setdefault(k, 0) + v
                    else:
                        result['Results']['RecordsPassed'] += 1
                if errcount:
                    result['Results']['ErrorDetails'].append(errcount)
                # Terminate the output file write consumer process if
                # applicable
                if prc:
                    self._outputqueue.put(None)
                    prc.join()
                    result['Results']['OutputFile'] = outputfile
            log.info('Process complete')
            runtime = round((time.time() - starttime)/60)
            log.info('Run time: {runtime} mins'.format(runtime=runtime))
            return result
        finally:
            if fo:
                fo.close()


# if __name__ == '__main__':
#     configfile = '/Users/ram.jayapalan/Downloads/test/test.ini'
#     sourcefile = '/Users/ram.jayapalan/Downloads/test/test_20200518.txt'
#     outputdir = '/Users/ram.jayapalan/Downloads/test/'
#     val = ValidateFile(configfile, sourcefile)
#     res = val.getresult(outputdir=outputdir)
#     print(res)
