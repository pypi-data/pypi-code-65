# Copyright (C) 2019 Majormode.  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import datetime
import logging
import psycopg2
import re

from majormode.perseus.model.enum import Enum
from majormode.perseus.model import obj
from majormode.perseus.model.obj import Serializable
from majormode.perseus.utils import cast


# Regular expression that matches any valid SQL comments such as:
#
# * comment that starts with the characters `--` and followed by any
#   characters until the end of the line.</li>
#
# * a C-like comment that starts with `/*` and ends with `*/`.
REGEX_SQL_COMMENT = re.compile(r'(--[^\n]*[\n])|(/\*([^/]|([^*]/))*\*/)|(/\*\*/)')

# Regular expression that matches a placeholder, also known as a named
# variable, within a parameterized SQL statement, such as:
#
# * `%(foo)s`: Element or list of elements.  For instance:
#
#       SELECT * FROM foo WHERE a = %(a)s
#
#       SELECT * FROM foo WHERE a IN (%(a)s)
#
# * `%[foo]s`: Nested list of elements.  For instance:
#
#       SELECT * FROM (VALUES %[a]s) AS foo(a, b)
#
PlaceholderType = Enum(
    'simple_list',
    'nested_list'
)

PATTERN_SQL_PLACEHOLDERS = {
    PlaceholderType.simple_list: r'%\(([^\)]*)\)s',
    PlaceholderType.nested_list: r'%\[([^\]]*)\]s'
}

REGEX_PATTERN_SQL_PLACEHOLDERS = re.compile('|'.join(PATTERN_SQL_PLACEHOLDERS.values()))


PATTERN_SQL_PLACEHOLDER_EXPRESSIONS = {
    PlaceholderType.simple_list: r'%%\(%s\)s',
    PlaceholderType.nested_list: r'%%\[%s\]s'
}


# PATTERN_SQL_PLACEHOLDERS = {
#     PlaceholderType.simple_list: PATTERN_SQL_PLACEHOLDER_SIMPLE_LIST,
#     PlaceholderType.nested_list: PATTERN_SQL_PLACEHOLDER_NESTED_LIST
# }


class RdbmsConnection(object):
    """
    Represent a connection to a Relational DataBase Management System
    (RDBMS)::

    ``python
    >>> with RdbmsConnection.acquire_connection() as connection:
    ...     cursor = connection.execute(
    ...         "SELECT a, b, c FROM foo WHERE a = %(a)s",
    ...         {'a': 1})
    ...
    ...     # Fetch one row from the result set.
    ...     row = cursor.fetch_one()
    ...
    ...     # Retrieve the value of the specified element from the row fetched.
    ...     a = row.get_value('a')
    ...
    ...     # Retrieve an object built from the row fetched where all the object's
    ...     # attributes correspond to the element of the row.
    ...     foo = row.get_object()
    ...     print(foo.a, foo.b, foo.c)
    ...
    ...     # Fetch all the remaining rows from the result set.
    ...     row_list = cursor.fetch_all()
    ``

    The `execute` method accepts several types of placeholders in SQL
    statements:

    * element: %(element)s

    * tuple of one element:

    * simple list:

    * nested list:

        connection.execute('''
            SELECT a, b, c
              FROM foo
              WHERE a = %(a)s
                AND b > %(b)s''',
            { 'a': 1
              'b': 'bar' })

        =>  SELECT a, b, c
              FROM foo
              WHERE a = 1
                AND b > 'bar'


        connection.execute('''
            SELECT a, b, c
              FROM foo
              WHERE c = %(c)s''',
            { 'c': ('ST_SetSRID(ST_MakePoint(160.1, 10.6), 4326))') })

        =>  SELECT a, b, c
              FROM foo
              WHERE c = ST_SetSRID(ST_MakePoint(160.1, 10.6), 4326))


        connection.execute('''
            SELECT a, b, c
              FROM foo
              WHERE a IN (%(a)s)''',
            { 'a': [1, 2, 3] }''')

        => SELECT a, b, c
              FROM foo
              WHERE a IN (1, 2, 3)


        connection.execute('''
            SELECT a, b, c
              FROM (VALUES %[values]s) AS foo(a, b, c)''',
            { 'values': [
                    [ 1, 'bar1', ('ST_SetSRID(ST_MakePoint(160.1, 10.6), 4326))') ],
                    [ 2, 'bar2', ('ST_SetSRID(ST_MakePoint(160.1, 10.6), 4326))') ],
                    [ 3, 'bar3', ('ST_SetSRID(ST_MakePoint(160.1, 10.6), 4326))') ] ] }''')

        => SELECT a, b, c
              FROM (VALUES (1, 'bar1', ST_SetSRID(ST_MakePoint(160.1, 10.6), 4326)),
                           (2, 'bar2', ST_SetSRID(ST_MakePoint(160.1, 10.6), 4326)),
                           (3, 'bar3', ST_SetSRID(ST_MakePoint(160.1, 10.6), 4326))) AS foo(a, b, c)

    """
    class DefaultConnectionPropertiesSettingException(Exception):
        """
        Signal that the settings of the connection properties to the default
        Relational DataBase Management System (Rdbms) have not been defined
        properly into the Python settings file.
        """
        pass

    class RdbmsCursor(object):
        """
        Represent a database cursor, which is used to manage the context of a
        fetch operation.  The native Python database cursor is embedded in
        this object.
        """
        def __init__(self, cursor):
            """
            Build a `RdbmsCursor` instance.


            :param cursor: a Python database cursor.
            """
            self.__native_cursor = cursor
            self.__column_index_dict = {} if cursor.description is None else \
                dict([
                    (cursor.description[column_index][0], column_index)
                    for column_index in range(len(cursor.description))])

        def fetch_one(self):
            """
            Fetch the next row of the query result set, returning a `RdbmsRow`
            instance, or `None` when no more data is available.


            :return: a `RdbmsRow` instance or `None` when no more data is
                available.
            """
            row = self.__native_cursor.fetchone()
            return row and RdbmsConnection.RdbmsRow(self.__column_index_dict, row)

        def fetch_all(self):
            """
            Fetch all remaining rows of the query result, returning a list of
            `RdbmsRow` instance.


            :return: a list of `RdbmsRow` instance.
            """
            return [RdbmsConnection.RdbmsRow(self.__column_index_dict, row)
                    for row in self.__native_cursor.fetchall()]

        def get_row_count(self):
            """
            Return the number of rows that the last `execute` produced.

            :return: the number of rows that the last `execute` produced, or
                `-1` in case no execute statement has been performed on the
                cursor.
            """
            return self.__native_cursor.rowcount

    class RdbmsObject(Serializable):
        """
        Represent a row fetched from the result of a query statement, where
        each member of this instance corresponds to a column that has been
        selected in the query statement.
        """
        def __init__(self, column_index_dict, row, cast_operators=None):
            """
            Build a `RdbmsRow` instance providing a database row and the
            description of the columns.


            :param column_index_dict: a dictionary where the key corresponds to
                the name of a column and the value references the index of this
                column in the row.

            :param row: a sequence of values that a query statement returned.

            :param cast_operators: dictionary of Python data types to which the
                values of some columns need to be casted to.  A key of the
                dictionary corresponds to the name of a column; the value
                corresponds to a Python class which constructor accepts a Unicode
                string, or a function, responsible to cast the column's value into
                the expected data type:

                    {
                      "account_id": uuid.UUID,
                      "coordinates": majormode.perseus.model.GeographicCoordinates
                    }
            """
            super().__init__()
            self.__dict__ = dict([
                (column_name,
                 RdbmsConnection.RdbmsObject.decode(
                     row[column_index],
                     cast_operators and cast_operators.get(column_name)))
                for column_name, column_index in column_index_dict.items()])

        @staticmethod
        def decode(value, cast_operator=None):
            if isinstance(value, datetime.datetime):
                value = str(value)

            if cast_operator:
                return cast.string_to_enum(value, cast_operator) if isinstance(cast_operator, Enum) \
                    else cast_operator(value)
            else:
                return value

    class RdbmsRow:
        """
        Represent a row fetched from the result of a query statement.
        """
        def __init__(self, column_index_dict, row):
            """
            Build a new `RdbmsRow` providing a database row and the description
            of the columns.

            :param column_index_dict: a dictionary where the key corresponds to
                the name of a column and the value references the index of this
                column in the row.

            :param row: a sequence of values that a query statement returned.
            """
            self.__column_index_dict = column_index_dict
            self.__row = row

        def get_object(self, cast_operators=None):
            """
            Return an `RdbmsObject` that represents a row fetched from the
            result of a query statement, where each member of this instance
            corresponds to a column that has been selected in the query statement.


            :param cast_operators: dictionary of Python data types to which the
                values of some columns need to be casted to.  A key of the
                dictionary corresponds to the name of a column; the value
                corresponds to a Python class which constructor accepts a Unicode
                string, or a function, responsible to cast the column's value into the
                expected data type:

                {
                  "account_id": uuid.UUID,
                  "coordinates": majormode.perseus.model.GeographicCoordinates
                }


            :return: an `RdbmsObject`.
            """
            return RdbmsConnection.RdbmsObject(self.__column_index_dict, self.__row, cast_operators)

        def get_value(self, column_name, cast_operator=None):
            """
            Return the value of the specified column.


            :param column_name: a column name.  Case is sensitive.

            :param cast_operator: a Python class which constructor accepts a
                Unicode string, or a function, responsible to cast the column's
                value into the expected data type:


            :return: the value of the column.
            """
            value = self.__row[self.__column_index_dict[column_name]]
            if cast_operator is None:
                return value

            return RdbmsConnection.RdbmsObject.decode(value, cast_operator=cast_operator)

    def __init__(self, hostname, port, database_name,
                 account_username, account_password,
                 logger_name=None,
                 auto_commit=False):
        """
        Build a `RdbmsConnection` instance providing properties of
        connection to Relational DataBase Management System (RDBMS).


        :param hostname: hostname of the RDBMS server to connect to.

        :param port: port number the RDBMS server listens at.

        :param database_name: name of the database to use.

        :param account_username: username of the database account on whose
            behalf the connection is being made to the RDBMS server.

        :param account_password: password of the user account.

        :param logger_name: name of the logger for debug information.

        :param auto_commit: indicate whether the transaction needs to be
            committed at the end of the session.
        """
        self.hostname = hostname
        self.port = port
        self.database_name = database_name
        self.account_username = account_username
        self.account_password = account_password
        self.__auto_commit = auto_commit

        self.__cursor = None

        self.logger_name = logger_name
        self.logger = logging.getLogger(self.logger_name)

        self._reference_count = 0

    def __enter__(self):
        """
        Enter the runtime context, open a connection to the RDBMS server, and
        return this object to allow `execute` to be used as the context
        expression in a `with` statement.


        :return: this `RdbmsConnection` object.
        """
        if self._reference_count == 0:
            self.__connection = psycopg2.connect(
                host=self.hostname,
                port=self.port,
                database=self.database_name,
                user=self.account_username,
                password=self.account_password)

        self._reference_count += 1

        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """
        Exit the runtime context and automatically close the connection to the
        RDBMS server.

        The parameters describe the exception that caused the context to be
        exited.  If the context was exited without an exception, all three
        arguments will be `None`.


        :param exception_type: the exception type of the exception being
            handled (a class object).

        :param exception_value: exception parameter (its associated value or
            the second argument to raise, which is always a class instance
            if the exception type is a class object).

        :param exception_traceback: a traceback object which encapsulates the
            call stack at the point where the exception originally occurred.


        :return: `False` to indicate whether, if an exception occurred while
            executing the body of the with statement, the exception has to
            continue propagating after this method has finished executing.
        """
        self._reference_count -= 1

        if self._reference_count == 0:
            if self.__auto_commit and exception_type is None:
                self.__connection.commit()

            self.__connection.close()

        return False  # Propagate the exception, if any.

    @staticmethod
    def acquire_connection(settings, tag=None, logger_name=None, auto_commit=False):
        """
        Return a connection to a Relational DataBase Management System (RDBMS)
        the most appropriate for the service requesting this connection.


        :param settings: A dictionary of connection properties::

                   {
                     None: {
                       'rdbms_hostname': "...",
                       'rdbms_port': ...,
                       'rdbms_database_name': "...",
                       'rdbms_account_username': '...'
                       'rdbms_account_password': '...'
                     },
                     'tag': {
                       'rdbms_hostname': "...",
                       'rdbms_port': ...,
                       'rdbms_database_name': "...",
                       'rdbms_account_username': '...'
                       'rdbms_account_password': '...'
                     },
                     ...
                   }
               The key `None` is the default tag.

        :param tag: a tag that specifies which particular connection properties
            has to be used.

        :param logger_name: name of the logger for debug information.

        :param auto_commit: indicate whether the transaction needs to be
            committed at the end of the session.


        :return: a `RdbmsConnection` instance to be used supporting the
            Python clause `with ...:`.


        :raise DefaultConnectionPropertiesSettingException: if the specified
            tag is not defined in the dictionary of connection properties,
            and when no default connection properties is defined either (tag `None`).
        """
        try:
            connection_properties = settings.get(tag, settings[None])
        except KeyError:
            raise RdbmsConnection.DefaultConnectionPropertiesSettingException()

        return RdbmsConnection(
                connection_properties['rdbms_hostname'],
                connection_properties['rdbms_port'],
                connection_properties['rdbms_database_name'],
                connection_properties['rdbms_account_username'],
                connection_properties['rdbms_account_password'],
                logger_name=logger_name,
                auto_commit=auto_commit)

    @property
    def auto_commit(self):
        return self.__auto_commit

    def commit(self):
        self.__connection.commit()

    def execute(
            self,
            sql_statement,
            parameters=None,
            allow_missing_placeholders=False):
        """
        Execute the specified Structured Query Language (SQL) parameterized
        statement.


        @note: each result column MUST be named with distinct names.


        :param sql_statement: a string representation of a Structured Query
            Language (SQL) expression including Python extended format codes,
            also known as "pyformat", and extended pyformat code.  The
            following forms are accepted:

            * `%(name)s`: indicate a simple value as for instance in::

                  INSERT INTO foo(bar)
                    VALUES (%(value)s)

              with `parameters`::

                  { 'value': 'something' }


            * `%[name]s`: indicate a list of simple values such as, for
              instance, in::

                  INSERT INTO foo(bar)
                    VALUES %[values]s

              with `parameters`::

                  { 'values': [ i for i in range(8) ] }

            * `%[name]s`: indicate a list of tuples as for instance in::

                  INSERT INTO foo(a, b, c)
                    VALUES %[values]s

              with `parameters`::

                  { 'values': [ [ 0, 'a', '!' ],
                                [ 1, 'b', '@' ]
                                [ 2, 'c', '#' ] ] }

            * `%[name]s`: indicate a list of tuples of `(boolean, value)`
              where:

              * `boolean`: `True` if the value MUST be used as it,
                `False` if the value needs to be quoted.

              * `value`: the value itself.

              as for instance in::

                  INSERT INTO foo(id, coordinates)
                    VALUES %[values]s

              with `parameters`::

                  { 'values': [ [ uuid.uuid1(), (False, 'ST_SetSRID(ST_MakePoint(160.1, 10.6), 4326)') ],
                                [ uuid.uuid1(), (False, 'ST_SetSRID(ST_MakePoint(160.1, 10.6), 4326)') ],
                                [ uuid.uuid1(), (False, 'ST_SetSRID(ST_MakePoint(160.1, 10.6), 4326)') ] ] }

        :param parameters: a dictionary of parameters.

        :param allow_missing_placeholders: Indicate whether some placeholders
            can be defined but not declared in the SQL query.  This may happen
            when a SQL query is programmatically generated depending on
            conditions while the placeholders for all the conditions are
            passed to the function.


        :return: a cursor object representing a database cursor, which is used
            to manage the context of a fetch operation.
        """
        if parameters:
            # Convert the simple value of parameters which the database adapter
            # cannot adapt to SQL type, such as enum values.
            # [http://initd.org/psycopg/docs/usage.html#query-parameters]
            #
            # @note: tuple is a special type used to indicate not to quote the
            #     underlying value which is a special SQL expression, such as a
            #     call of a stored procedure.
            for (name, value) in parameters.items():
                if not isinstance(value, (type(None), bool, int, float, str, tuple, list, set)):
                    parameters[name] = obj.stringify(value)

            # Replace the placeholders in the SQL statement for which the database
            # adapter cannot adapt the Python value to SQL types, for instance,
            # list and nested list.
            sql_statement = RdbmsConnection.__prepare_statement(
                sql_statement,
                parameters,
                allow_missing_placeholders=allow_missing_placeholders)

        # Compact the SQL statement expression removing useless space and
        # newline characters, and stripping all SQL comments.
        sql_statement = ' '.join(
            [line
             for line in [
                line.strip()
                for line in REGEX_SQL_COMMENT.sub('\n', sql_statement.strip()).splitlines()]
             if len(line) > 0])

        self.logger.debug(f'Executing SQL statement:\n{sql_statement}\n\twith: {parameters}')

        if self.__cursor is None:
            self.__cursor = self.__connection.cursor()

        execution_start_time = datetime.datetime.now()
        self.__cursor.execute(sql_statement, parameters)
        execution_end_time = datetime.datetime.now()
        execution_duration = execution_end_time - execution_start_time

        execution_duration_milliseconds = execution_duration.seconds * 1000 + \
            execution_duration.microseconds / 1000
        self.logger.debug(f'Time: {execution_duration_milliseconds} ms')

        return RdbmsConnection.RdbmsCursor(self.__cursor)

    def rollback(self):
        self.__connection.rollback()

    @staticmethod
    def __expand_placeholder_value(value):
        """
        Return the SQL string representation of the specified placeholder's
        value.


        :param value: the value of a placeholder such as a simple element, a
            list, or a tuple of one string.


        @note: by convention, a tuple of one string indicates that this string
            MUST not be quoted as it represents, for instance, a called to
            a stored procedure, and not a textual content to modify into a
            table.


        :return: a SQL string representation.
        """
        if isinstance(value, (list, set)) or (isinstance(value, tuple) and len(value) != 1):
            sql_value = ','.join([
                RdbmsConnection._to_sql_value(
                    element if not isinstance(element, tuple) else element[0],
                    noquote=isinstance(element, tuple))
                for element in value])

        elif isinstance(value, tuple):
            assert len(value) == 1
            value = value[0]
            assert value is None or isinstance(value, str), f'String expected instead of {type(value)}'
            sql_value = RdbmsConnection._to_sql_value(value, True)

        else:
            sql_value = RdbmsConnection._to_sql_value(value)

        return sql_value

    @staticmethod
    def __get_placeholders(sql_statement, parameters, allow_missing_placeholders=False):
        """
        Retrieve the list of placeholders and their type defined in an SQL
        statement.


        :param sql_statement: a parameterized statement.

        :param parameters: the list of parameters used in the SQL statement.

        :param allow_missing_placeholders: Indicate whether some placeholders
            can be defined but not declared in the SQL query.  This may happen
            when a SQL query is programmatically generated depending on
            conditions while the placeholders for all the conditions are
            passed to the function.


        :return: a dictionary of placeholders where the key represents the
            name of a placeholder, the value corresponds to a tuple::

                (`type:PlaceholderType`, `value`)

            where :

            * `type`: type of the placeholder

            * `value`: value to replace the placeholder.
        """
        # Find the list of placeholders, and their type, defined in the SQL
        # statement.
        placeholders = {}

        try:
            for match in REGEX_PATTERN_SQL_PLACEHOLDERS.findall(sql_statement):
                for i, placeholder_type in enumerate(PlaceholderType):
                    placeholder_name = match[i]
                    if placeholder_name:
                        placeholder_value = parameters[placeholder_name]

                        # Check that the value of the corresponding parameter is a list.
                        if placeholder_type == PlaceholderType.nested_list \
                            and (isinstance(placeholder_value, tuple) and len(placeholder_value) == 1) \
                            and not isinstance(placeholder_value, (list, set, tuple)):
                            raise ValueError(f"The value of the placeholder '{placeholder_name}' must be a list")

                        placeholders[placeholder_name] = (placeholder_type, placeholder_value)
                        break
        except KeyError:
            raise ValueError(f'The placeholder {placeholder_name} is not defined as a parameter')

        if not allow_missing_placeholders:
            # Check whether all the specified parameters have their corresponding
            # placeholder in the SQL statement.
            undefined_placeholders = [
                parameter
                for parameter in parameters
                if parameter not in placeholders]

            if undefined_placeholders:
                raise ValueError(
                    'The placeholders %s are missing from the extended pyformat SQL statement\n%s' %
                    (', '.join(['"%s"' % _ for _ in undefined_placeholders]), sql_statement))

        return placeholders

    @staticmethod
    def __prepare_statement(sql_statement, parameters, allow_missing_placeholders=False):
        """
        Prepare the specified SQL statement, replacing the placeholders by the
        value of the given parameters

        :param sql_statement: the string expression of a SQL statement.

        :param parameters: a dictionary of parameters where the key represents
            the name of a parameter and the value represents the value of this
            parameter to replace in each placeholder of this parameter in the
            SQL statement.

        :param allow_missing_placeholders: Indicate whether some placeholders
            can be defined but not declared in the SQL query.  This may happen
            when a SQL query is programmatically generated depending on
            conditions while the placeholders for all the conditions are
            passed to the function.


        :return: a string representation of the SQL statement where the
            placeholders have been replaced by the value of the corresponding
            variables, depending on the type of these variables.
        """
        placeholders = RdbmsConnection.__get_placeholders(
            sql_statement,
            parameters,
            allow_missing_placeholders=allow_missing_placeholders)

        for (variable_name, (variable_type, variable_value)) in placeholders.items():
            # Only expand parameters whose value corresponds to a list.
            if isinstance(variable_value, (list, set, tuple)):
                sql_statement = RdbmsConnection._replace_placeholder(
                    sql_statement,
                    (variable_name, variable_type, variable_value))

                # Remove this parameter as it has been expended in the SQL expression.
                del parameters[variable_name]

        return sql_statement

    @staticmethod
    def _replace_placeholder(sql_statement, variable):
        """
        Return the string obtained by replacing the specified placeholders by
        its corresponding value.


        :param sql_statement: the string expression of a SQL statement to
            replace placeholders with their corresponding values.

        :param variable: the variable to use to replace the corresponding
            placeholder(s) in the SQL statement.

            * `name`: name of the variable.

            * `type`: an instance of `PlaceholderType`.

            * `value`: the value of this variable to replace the corresponding
              placeholder(s) of this variable in the SQL statement.


        :return: a string expression of the SQL statement where the
            paceholders of the specified variable have been replace by the
            value of this variable, depending on the type of this varialble.
        """
        variable_name, variable_type, variable_value = variable

        sql_value = RdbmsConnection.__expand_placeholder_value(variable_value) \
            if variable_type == PlaceholderType.simple_list \
            else ','.join(['(%s)' % RdbmsConnection.__expand_placeholder_value(v) for v in variable_value])

        return re.sub(PATTERN_SQL_PLACEHOLDER_EXPRESSIONS[variable_type] % variable_name, sql_value, sql_statement)

    @staticmethod
    def _to_sql_value(value, noquote=False):
        """
        Return the SQL string representation of the specified value.


        :param value: a value to convert into its SQL string representation.

        :param noquote: indicate whether to quote or not the specified value.


        :return: a SQL string representation of the specified value.
        """
        # Convert to string the values that the database adapter can't adapt
        # to a SQL type.
        # [http://initd.org/psycopg/docs/usage.html#query-parameters]
        if not isinstance(value, (type(None), bool, int, float, str)):
            value = obj.stringify(value)

        if noquote:
            return value

        # @warning: do not use `psycopg2.extensions.adapt(value).getquoted()`
        #     because it returns `str` object, which is expected as adaptation
        #     is taking a Python object and converting it into a SQL
        #     representation: this is always a bytes string, as it has to be
        #     sent to the socket.  However the caller might not use the quoted
        #     value to immediately sent it to the database server, but it can
        #     use it for rewriting an SQL statement, which will break the text
        #     encoding.
        return 'NULL' if value is None \
            else '%s' % str(value) if isinstance(value, (bool, int, float)) \
            else "e'%s'" % value.replace("'", "''").replace('\\', '\\\\').replace('%', '%%')
