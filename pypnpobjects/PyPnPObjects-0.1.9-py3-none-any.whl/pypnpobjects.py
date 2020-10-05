import os
import re
from types import GeneratorType
import subprocess as sp
from ast import literal_eval
import sqlite3
import json
import atexit


if os.sys.platform.upper() != 'WIN32':
    raise OSError('`WMIDEVINFO` is supported in WIN32 only, not on `{0}`'.format(os.sys.platform))


if os.sys.version_info[0] == 2:
    FileNotFoundError = IOError
    TimeoutError = EnvironmentError

class WMIStorePNPObjectsException(Exception):
    def __init__(self, err):
        super(WMIStorePNPObjectsException, self).__init__(err)

class WMIInternalPNPObjectProperties(object):
    def __getattr__(self, attr):
        return self.__keys.get(attr.lower(), ''), self.__data.get(self.__keys[attr.lower()], '')
    def __getitem__(self, k):
        return self.__keys.get(k.lower(), ''), self.__data.get(self.__keys[k.lower()], '')
    def __contains__(self, k):
        return k.lower() in self.__keys.keys()
    def __iter__(self):
        return iter(item for item in self.__data.items() if not item[0].startswith('_'))
    def __len__(self):
        return len(self.__data)
    def __init__(self, **kwargv):
        self.__data = kwargv
        self.__keys = {k.lower() : k for k in kwargv.keys()}


class WMIStorePNPObjects(object):

    
    @staticmethod
    def _getSupportedDateFormat(datestr):
        pass

    @staticmethod
    def _isCommandAcceptable(object_):
        return (isinstance(object_, list) or isinstance(object_, tuple) or isinstance(object_, GeneratorType))
        
    @staticmethod
    def _isValidCMDPart(object_):
        if isinstance(object_, str) or isinstance(object_, int) or isinstance(object_, float) or isinstance(object_, bool):
            return True
        else:
            os.sys.stderr.write("Ignoring command part `{0}`, since it is a invalid type\n".format(object_))
            return False
    def __repr__(self):
        return 'WMIStorePNPObjects object at {0} <{1}>'.format(hex(id(self)), ' '.join(
            ['{1}{0}{1}'.format(cmd_part, '"' if (' ' in cmd_part or '\t' in cmd_part) else '') for cmd_part in self.__command_list]
            ))
    def __enter__(self):
        return self
    
    def __init__(self, command = ["Get-WmiObject", "Win32_PnPEntity"]):
        self.__command_list = []
        self._conn = None
        if isinstance(command, str):
            pat = r'(?:([\'\"])(.*?)(?<!\\)(?:\>\\\\)*\1|([^\s]+))'
            matches = re.findall(pat, command)
            for match in matches:
                self.__command_list += [cmd_part for cmd_part in match if cmd_part.strip() not in(
                    '"', "'", "", None
                )]
        else:
            if not WMIStorePNPObjects._isCommandAcceptable(command):
                raise TypeError('{0}.__init__ expects one `string` or `list kind` object as a positional argument'.format('WMICommand'))
            self.__command_list = [str(cmd_part) for cmd_part in command if WMIStorePNPObjects._isValidCMDPart(cmd_part)]
        if len(self.__command_list) == 0:
            raise WMIStorePNPObjectsException('Invalid 0-length command')
        if self.__command_list[0].upper() != 'POWERSHELL':
            self.__command_list.insert(0, 'powershell')
    def free(self):
        try:
            self._conn.close()
        except:
            pass
    def __exit__(self, type_, value_, tb_):
        if os.sys.version_info[0] == 3:
            atexit.unregister(self.free)
        else:
            for handler in atexit._exithandlers:
                if handler[0] == self.free:
                    del handler
                pass
        self.free()
        pass
    
    def query(self, *select, **where):
        '''
        description: Query the required fields from the database connection
        usage: self._conn, database connection from which we need to query the object's properties
                select, list of object's properties which are required to fetched from database,
                    if empty, all the fields will be selected
                whare, basically where condition which will be used as condition of where clause.
                comparision_operator ['equal' | 'like' ], default is 'equal', if 'like', we will compare
                    with SQL pattern matching
                case_sensitive_comparision [ True | False], default is True, if set to False, where
                    conditions will be case insentive comparision
        Reference: https://docs.microsoft.com/en-us/windows/win32/cimwin32prov/win32-pnpentity
        '''
        comparision_operator = where.pop('comparision_operator', 'equal')
        if not isinstance(comparision_operator, str):
            comparision_operator = 'equal'
        elif comparision_operator.lower().strip() not in ('equal', 'like'):
            comparision_operator = 'equal'

        if comparision_operator == 'equal': comparision_operator = '='

        case_sensitive_comparision = where.pop('case_sensitive_comparision', True)
        if not isinstance(case_sensitive_comparision, bool):
            if isinstance(case_sensitive_comparision, (int, float)):
                case_sensitive_comparision = case_sensitive_comparision != 0
            elif isinstance(case_sensitive_comparision, str):
                if case_sensitive_comparision.strip().title() in ('True', 'False'):
                    case_sensitive_comparision = literal_eval(case_sensitive_comparision)
                else:
                    case_sensitive_comparision = True
            else:
                case_sensitive_comparision = True
        if len(select) == 0:
            select = ('*', )

        fields = set()

        if len(select) <= 0:
            raise WMIStorePNPObjectsException('Atleast one field need to be select')
        for field in select:
            if isinstance(field, int) and field >= 0:
                try:
                    field_ = self._columns[field]
                    fields.add(field_)
                except IndexError:
                    raise WMIStorePNPObjectsException('Invalid column index %d, out of range'%(field))
            elif isinstance(field, str):
                if field.strip() == '*':
                    fields.clear()
                    fields = set(self._columns)
                    continue
                if field.lower().strip() in [f.lower() for f in self._columns]:
                    fields.add(field)
                else:
                    raise WMIStorePNPObjectsException('Invalid column name %s'%(field))
            else:
                raise WMIStorePNPObjectsException("Invalid column type `%s` of `%s`, must be string or int between 0 to %d"%(
                    type(field), field, len(self._columns)))
        select_query = 'SELECT {0} FROM {1}'.format(', '.join(fields), self._table)
        
        where_conds = []
        for cond_col, cond_val in where.items():
            if isinstance(cond_col, str):
                if cond_col.lower().strip() in [f.lower() for f in self._columns]:
                    where_conds.append('{0} {1} :{0} {2}'.format(
                        cond_col,
                        'is' if cond_val is None else comparision_operator,
                        'COLLATE NOCASE' if not case_sensitive_comparision else 'COLLATE BINARY')
                    )
                else:
                    raise WMIStorePNPObjectsException('Invalid column name %s used as a where condition'%(cond_col, ))
            else:
                raise WMIStorePNPObjectsException('Invalud column type `{0}` used as a where condition'.format(type(cond_col)))
        if len(where_conds) > 0:
            cond_str = ' WHERE ' + ' AND '.join(where_conds)
            select_query += cond_str
        try:
            cur = self._conn.cursor()
            if case_sensitive_comparision and comparision_operator.lower().strip() == 'like':
                cur.execute('PRAGMA case_sensitive_like = true;')
            cur.execute(select_query, where)
            output = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            if case_sensitive_comparision and comparision_operator.lower().strip() == 'like':
                cur.execute('PRAGMA case_sensitive_like = false;')
            cur.close()
        except Exception as e:
            raise WMIStorePNPObjectsException('Error occurred while executing the query : %s'%(str(e)))
        for result in output:
            yield WMIInternalPNPObjectProperties(**dict(zip(columns, result)))


    def load(self, db = ':memory:', table = 'Win32_PnPEntity', expected_exit_code = 0, timeout = 30):
        '''
        description: Loads all the pnp entity to the database
        usage: db [':memory:' | ':file:'], default is ':memory:' but if ':file:', a database file will be created
                                            with the name `win32_pnpentity.sqlite.db` inside CWD.
                table [sqlite table name], default is `Win32_PnPEntity`, which is the table name for storing the Objects
                                            and it's details
                expected_exit_code, default is `0`, should be an integer and if set to any other integer value,
                                            program is expected to have exit with same code
                timeout, default is `30`, should be an integer, time limit to find and run the executable only for python 3
        '''
        if not isinstance(db, str):
            db = ':memory:'
        db = db.lower().strip()
        if db not in (':memory:', ':file:'):
            db = ':memory:'
        if db == ':file:':
            db = os.path.abspath(os.path.join(os.getcwd(), 'win32_pnpentity.sqlite.db'))

        if not isinstance(table, str):
            self._table = 'Win32_PnPEntity'
        else:
            self._table = table.strip()
        if re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)', table) is None:
            self._table = 'Win32_PnPEntity'
        
        if not isinstance(timeout, int):
            timeout = 30
        elif timeout < 0:
            timeout = 30

        try:
            popen_argv = {
                'stdout' : sp.PIPE,
                'stderr' : sp.PIPE,
                'universal_newlines' : True,
                'bufsize' : 1
            }
            if os.sys.version_info[0] == 3:
                if os.sys.version_info[1] >= 7:
                    popen_argv['text'] = True
            
            proc = sp.Popen(self.__command_list, **popen_argv)

            if os.sys.version_info[0] == 3:
                out, err = proc.communicate(timeout=timeout)
            else:
                out, err = proc.communicate()
            ret = proc.wait()
            dev_list = None
            if ret == expected_exit_code and err.strip() == '':
                dev_list, datatypes = self._parseCommandResult(out)
            else:
                return (ret, err)
        except (TimeoutError, FileNotFoundError) as e:
            return (None, str(e))
        if isinstance(dev_list, list):
            column_dt = [' '.join(column_datatype) for column_datatype in datatypes.items()]
            ddl_columns = ', '.join(column_dt)

            check_constraints = []
            for column, datatype in datatypes.items():
                if datatype == 'BOOLEAN':
                    check_constraints.append(
                        '({0} IN(0, 1) or {0} IS NULL)'.format(column)
                    )
                elif datatype == 'DATETIME':
                    check_constraints.append(
                        r'''(({0} IS strftime('%Y-%m-%d %H:%M:%S', {0}))
                            OR ({0} IS strftime('%Y-%m-%d', {0})))'''.format(column)
                    )
            ddl_columns += ', CHECK({0})'.format(' AND '.join(check_constraints))

            
            create_win32_pnp_entity = r'''CREATE TABLE {0} ({1})'''.format(self._table, ddl_columns)
            # print create_win32_pnp_entity
            insert_win32_pnp_entity = r'''
            INSERT INTO {0}({1}) VALUES({2});
            '''
            self._columns = dev_list[0].keys()
            try:
                self._conn = sqlite3.connect(db)
                cur = self._conn.cursor()
                cur.execute('DROP TABLE IF EXISTS {0};'.format(self._table))
                cur.execute(create_win32_pnp_entity)
                column_str = ', '.join(self._columns)
                column_to_data_map = ':' + ', :'.join(self._columns)
                cur.executemany(insert_win32_pnp_entity.format(
                    self._table, column_str, column_to_data_map
                ), dev_list)
                self._conn.commit()
                cur.close()
                err = None
                atexit.register(self.free)
            except Exception as e:
                self._conn = None
                err = str(e) 
        else:
            self._conn = None
            err = 'Empty device list, could not parse'
        return (ret, err)
    def _parseCommandResult(self, result):
        datatypes = dict()
        dev_list = []
        dev_list.append(dict())
        lines = (line.strip() for line in result.strip().split('\n') if not line.strip().startswith('__'))
        pat = r'^([a-zA-Z0-9]+)\s*\:\s*(.*)$'
        last_key = ''

        for line in lines:
            isBoolean = False
            if line == '':
                last_key = ''
                dev_list.append(dict())
                continue
            mt = re.match(pat, line)
            if mt is not None:
                key, value = [d.strip() for d in mt.groups()]
                if value.upper() in ('FALSE', 'TRUE'):
                    value = value.lower().title()
                try:
                    if value == '':
                        value = 'None'
                    value = literal_eval(value)
                    if isinstance(value, bool):
                        isBoolean = True
                        value = int(value)
                except (ValueError, SyntaxError, WindowsError):
                    pass
                finally:
                    last_key = key
                    if value is None:
                        if key not in datatypes.keys():
                            if key.upper() == 'INSTALLDATE':
                                datatypes[key] = 'DATETIME'
                            else:
                                datatypes[key] = 'UNKNOWN'
                    elif isinstance(value, str):
                        if key.upper() == 'INSTALLDATE':
                            datatypes[key] = 'DATETIME'
                        else:
                            datatypes[key] = 'TEXT'
                    elif isinstance(value, int):
                        if key not in datatypes.keys():
                            if isBoolean:
                                datatypes[key] = 'BOOLEAN'
                            else:
                                datatypes[key] = 'INTEGER'
                        elif datatypes[key] == 'UNKNOWN':
                            datatypes[key] = 'INTEGER'
                    dev_list[-1][key] = value
            else:
                try:
                    dev_list[-1][last_key] += ' ' + line
                except KeyError:
                    pass
        datatypes = {column : 'TEXT' if datatype == 'UNKNOWN' else datatype for column, datatype in datatypes.items()}

        return dev_list, datatypes
