# Imports

from ..commands import Command

# Exports

__all__ = (
    "MYSQL_MAPPINGS",
    "mysql_create",
    "mysql_drop",
    "mysql_dump",
    "mysql_exec",
    "mysql_exists",
    "mysql_grant",
    "mysql_user",
)

# Functions


def _get_mysql_command(host="localhost", name="mysql", password=None, port=3306, user="root"):
    a = list()
    a.append("%s --user=%s" % (name, user))
    a.append("--host=%s" % host)
    a.append("--port=%s" % port)

    if password:
        a.append('--password="%s"' % password)

    return a


def mysql_create(database, host="localhost", owner=None, password=None, port=3306, user="root", **kwargs):
    """Create a MySQL database.

    - database (str): The database name.
    - host (str): The database host name or IP address.
    - password (str): The password for the user with sufficient access privileges to execute the command.
    - owner (str): The owner (user/role name) of the new database.
    - port (int): The TCP port number of the MySQL service running on the host.
    - user (str): The name of the user with sufficient access privileges to execute the command.

    """
    kwargs.setdefault("comment", "create the %s mysql database" % database)

    # MySQL commands always run without sudo because the --user may be provided.
    kwargs['sudo'] = False

    # Assemble the command.
    a = _get_mysql_command(host=host, name="mysqladmin", password=password, port=port, user=user)
    a.append("create %s" % database)

    if owner:
        grant = mysql_grant(
            owner,
            database=database,
            host=host,
            password=password,
            port=port,
            user=user,
        )
        a.append("&& %s" % grant.get_statement(suppress_comment=True))

    return Command(" ".join(a), **kwargs)


def mysql_drop(database, host="localhost", password=None, port=3306, user="root", **kwargs):
    """Drop (remove) a MySQL database.

    - database (str): The database name.
    - host (str): The database host name or IP address.
    - password (str): The password for the user with sufficient access privileges to execute the command.
    - port (int): The TCP port number of the MySQL service running on the host.
    - user (str): The name of the user with sufficient access privileges to execute the command.

    """
    kwargs.setdefault("comment", "remove the %s mysql database" % database)

    # MySQL commands always run without sudo because the --user may be provided.
    kwargs['sudo'] = False

    # Assemble the command.
    a = _get_mysql_command(host=host, name="mysqladmin", password=password, port=port, user=user)
    a.append("drop %s" % database)

    return Command(" ".join(a), **kwargs)


def mysql_dump(database, file_name=None, host="localhost", inserts=False, password=None, port=3306, user="root",
               **kwargs):
    """Dump (export) a MySQL database.

    - database (str): The database name.
    - host (str): The database host name or IP address.
    - password (str): The password for the user with sufficient access privileges to execute the command.
    - port (int): The TCP port number of the MySQL service running on the host.
    - user (str): The name of the user with sufficient access privileges to execute the command.

    """
    kwargs.setdefault("comment", "dump the %s mysql database" % database)

    # MySQL commands always run without sudo because the --user may be provided.
    # kwargs['sudo'] = False

    # Assemble the command.
    a = _get_mysql_command(host=host, name="mysqldump", password=password, port=port, user=user)

    # if data_only:
    #     a.append("--no-create-info")
    # elif schema_only:
    #     a.append("--no-data")
    # else:
    #     pass

    if inserts:
        a.append("--complete-inserts")

    a.append(database)

    _file_name = file_name or "%s.sql" % database
    a.append("> %s" % _file_name)

    return Command(" ".join(a), **kwargs)


def mysql_exec(sql, database="default", host="localhost", password=None, port=3306, user="root", **kwargs):
    """Execute a MySQL statement.

    - sql (str): The SQL to run.
    - database (str): The name of the database.
    - host (str): The host name.
    - password (str): The password for the user with sufficient access privileges to execute the command.
    - port (int): The TCP port number.
    - user (str): The name of the user with sufficient access privileges to execute the command.

    """
    kwargs['sudo'] = False
    kwargs.setdefault("comment", "execute mysql statement")

    a = _get_mysql_command(host=host, password=password, port=port, user=user)
    a.append('--execute="%s"' % sql)
    a.append(database)

    return Command(" ".join(a), **kwargs)


def mysql_exists(database, host="localhost", password=None, port=3306, user="root", **kwargs):
    """Determine if a MySQL database exists.

    - database (str): The database name.
    - host (str): The database host name or IP address.
    - password (str): The password for the user with sufficient access privileges to execute the command.
    - port (int): The TCP port number of the MySQL service running on the host.
    - user (str): The name of the user with sufficient access privileges to execute the command.

    """
    kwargs.setdefault("comment", "determine if the %s mysql database exists" % database)
    kwargs.setdefault("register", "mysql_database_exists")

    # MySQL commands always run without sudo because the --user may be provided.
    kwargs['sudo'] = False

    # Assemble the command.
    a = _get_mysql_command(host=host, password=password, port=port, user=user)

    sql = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '%s'" % database
    a.append('--execute="%s"' % sql)

    return Command(" ".join(a), **kwargs)


def mysql_grant(to, database=None, host="localhost", password=None, port=3306, privileges="ALL", user="root", **kwargs):
    """Grant privileges to a user.

    - to (str): The user name to which privileges are granted.
    - database (str): The database name.
    - host (str): The database host name or IP address.
    - password (str): The password for the user with sufficient access privileges to execute the command.
    - port (int): The TCP port number of the MySQL service running on the host.
    - privileges (str): The privileges to be granted.
    - user (str): The name of the user with sufficient access privileges to execute the command.

    """
    kwargs.setdefault("comment", "grant mysql privileges to %s" % to)

    a = _get_mysql_command(host=host, password=password, port=port, user=user)

    # See https://dev.mysql.com/doc/refman/5.7/en/grant.html
    _database = database or "*"
    sql = "GRANT %(privileges)s ON %(database)s.* TO '%(user)s'@'%(host)s'" % {
        'database': _database,
        'host': host,
        'privileges': privileges,
        'user': to,
    }
    a.append('--execute="%s"' % sql)

    return Command(" ".join(a))


def mysql_user(name, host="localhost", op="create", passwd=None, password=None, port=3306, user="root", **kwargs):
    """Work with a MySQL user.

    - name (str): The user name.
    - host (str): The host name.
    - op (str): The operation to perform: ``create``, ``drop``, ``exists``.
    - passwd (str): The password for a new user.
    - password (str): The password for the user with sufficient access privileges to execute the command.
    - port (int): The TCP port number.
    - user (str): The name of the user with sufficient access privileges to execute the command.

    """
    kwargs['sudo'] = False
    if op == "create":
        kwargs.setdefault("comment", "create %s mysql user" % name)

        a = _get_mysql_command(host=host, password=password, port=port, user=user)
        sql = "CREATE USER IF NOT EXISTS '%(user)s'@'%(host)s'" % {
            'host': host,
            'user': name,
        }
        if passwd:
            sql += " IDENTIFIED BY PASSWORD('%s')" % passwd

        a.append('--execute="%s"' % sql)

        return Command(" ".join(a), **kwargs)
    elif op == "drop":
        kwargs.setdefault("comment", "drop %s mysql user" % name)

        a = _get_mysql_command(host=host, password=password, port=port, user=user)

        sql = "DROP USER IF EXISTS '%(user)s'@'%(host)s'" % {
            'host': host,
            'user': name,
        }
        a.append('--execute="%s"' % sql)

        return Command(" ".join(a), **kwargs)
    elif op == "exists":
        kwargs.setdefault("comment", "determine if %s mysql user exists" % name)
        kwargs.setdefault("register", "mysql_user_exists")

        a = _get_mysql_command(host=host, password=password, port=port, user=user)

        sql = "SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '%s')" % name
        a.append('--execute="%s"' % sql)

        return Command(" ".join(a), **kwargs)
    else:
        raise NameError("Unrecognized or unsupported MySQL user operation: %s" % op)


MYSQL_MAPPINGS = {
    'mysql.create': mysql_create,
    'mysql.drop': mysql_drop,
    'mysql.dump': mysql_dump,
    'mysql.exists': mysql_exists,
    'mysql.grant': mysql_grant,
    'mysql.sql': mysql_exec,
    'mysql.user': mysql_user,
}
