# Imports

from ..commands import Command

# Exports

__all__ = (
    "PGSQL_MAPPINGS",
    "pgsql_create",
    "pgsql_drop",
    "pgsql_dump",
    "pgsql_exec",
    "pgsql_exists",
    "pgsql_user",
)

# Functions


def _get_pgsql_command(name, host="localhost", password=None, port=5432, user="postgres"):
    """Get a postgres-related command using commonly required parameters.

    :param name: The name of the command.
    :type name: str

    :param host: The host name.
    :type host: str

    :param password: The password to use.
    :type password: str

    :param port: The TCP port number.
    :type port: int

    :param user: The user name that will be used to execute the command.

    :rtype: list[str]

    """
    a = list()

    if password:
        a.append('export PGPASSWORD="%s" &&' % password)

    a.append(name)

    a.append("--host=%s" % host)
    a.append("--port=%s" % port)
    a.append("--username=%s" % user)

    return a


def pgsql_create(database, admin_pass=None, admin_user="postgres", host="localhost", owner=None, port=5432, template=None,
              **kwargs):
    """Create a PostgreSQL database.

    - database (str): The database name.
    - admin_pass (str): The password for the user with sufficient access privileges to execute the command.
    - admin_user (str): The name of the user with sufficient access privileges to execute the command.
    - host (str): The database host name or IP address.
    - owner (str): The owner (user/role name) of the new database.
    - port (int): The port number of the Postgres service running on the host.
    - template (str): The database template name to use, if any.

    """
    _owner = owner or admin_user

    # Postgres commands always run without sudo because the -U may be provided.
    kwargs['sudo'] = False

    # Assemble the command.
    base = _get_pgsql_command("createdb", host=host, password=admin_pass, port=port)
    base.append("--owner=%s" % _owner)

    if template is not None:
        base.append("--template=%s" % template)

    base.append(database)

    return Command(" ".join(base), **kwargs)


def pgsql_drop(database, admin_pass=None, admin_user="postgres", host="localhost", port=5432, **kwargs):
    """Remove a PostgreSQL database.

    - database (str): The database name.
    - admin_pass (str): The password for the user with sufficient access privileges to execute the command.
    - admin_user (str): The name of the user with sufficient access privileges to execute the command.
    - host (str): The database host name or IP address.
    - port (int): The port number of the Postgres service running on the host.

    """
    # Postgres commands always run without sudo because the -U may be provided.
    kwargs['sudo'] = False

    # Assemble the command.
    base = _get_pgsql_command("dropdb", host=host, password=admin_pass, port=port, user=admin_user)
    base.append(database)

    return  Command(" ".join(base), **kwargs)


def pgsql_dump(database, admin_pass=None, admin_user="postgres", file_name=None, host="localhost", port=5432, **kwargs):
    """Export a Postgres database.

    - database (str): The database name.
    - admin_pass (str): The password for the user with sufficient access privileges to execute the command.
    - admin_user (str): The name of the user with sufficient access privileges to execute the command.
    - file_name (str): The name/path of the export file. Defaults the database name plus ``.sql``.
    - host (str): The database host name or IP address.
    - port (int): The port number of the Postgres service running on the host.

    """
    _file_name = file_name or "%s.sql" % database

    # Postgres commands always run without sudo because the -U may be provided.
    # kwargs['sudo'] = False

    # Assemble the command.
    base = _get_pgsql_command("pg_dump", host=host, password=admin_pass, port=port, user=admin_user)
    base.append("--column-inserts")
    base.append("--file=%s" % _file_name)
    base.append(database)

    return Command(" ".join(base), **kwargs)


def pgsql_exec(sql, database="template1", host="localhost", password=None, port=5432, user="postgres", **kwargs):
    """Execute a psql command.

    - sql (str): The SQL to be executed.
    - database (str): The database name.
    - admin_pass (str): The password for the user with sufficient access privileges to execute the command.
    - admin_user (str): The name of the user with sufficient access privileges to execute the command.
    - host (str): The database host name or IP address.
    - port (int): The port number of the Postgres service running on the host.

    """
    # Postgres commands always run without sudo because the -U may be provided.
    kwargs['sudo'] = False

    # Assemble the command.
    base = _get_pgsql_command("psql", host=host, password=password, port=port, user=user)
    base.append("--dbname=%s" % database)
    base.append('-c "%s"' % sql)

    return Command(" ".join(base), **kwargs)


def pgsql_exists(database, admin_pass=None, admin_user="postgres", host="localhost", port=5432, **kwargs):
    """Determine if a Postgres database exists.

    - database (str): The database name.
    - admin_pass (str): The password for the user with sufficient access privileges to execute the command.
    - admin_user (str): The name of the user with sufficient access privileges to execute the command.
    - host (str): The database host name or IP address.
    - owner (str): The owner (user/role name) of the new database.
    - port (int): The port number of the Postgres service running on the host.

    """
    # Postgres commands always run without sudo because the -U may be provided.
    kwargs['sudo'] = False
    kwargs.setdefault("register", "pgsql_db_exists")

    base = _get_pgsql_command("psql", host=host, password=admin_pass, port=port, user=admin_user)
    base.append(r"-lqt | cut -d \| -f 1 | grep -qw %s" % database)

    return Command(" ".join(base), **kwargs)


def pgsql_user(name, admin_pass=None, admin_user="postgres", host="localhost", op="create", password=None, port=5432, **kwargs):
    """Work with a PostgreSQL user.

    - name (str): The user name.
    - host (str): The host name.
    - op (str): The operation to perform: ``create``, ``drop``, ``exists``.
    - passwd (str): The password for a new user.
    - password (str): The password for the user with sufficient access privileges to execute the command.
    - port (int): The TCP port number.
    - user (str): The name of the user with sufficient access privileges to execute the command.

    """
    # Postgres commands always run without sudo because the -U may be provided.
    kwargs['sudo'] = False

    if op == "create":
        kwargs.setdefault("comment", "create %s postgres user" % name)
        # Assemble the command.
        base = _get_pgsql_command("createuser", host=host, password=admin_pass, port=port)
        base.append("-DRS")
        base.append(name)

        if password is not None:
            base.append("&& psql -h %s -U %s" % (host, admin_user))
            base.append("-c \"ALTER USER %s WITH ENCRYPTED PASSWORD '%s';\"" % (name, password))

        return Command(" ".join(base), **kwargs)
    elif op == "drop":
        kwargs.setdefault("comment", "drop %s postgres user" % name)
        base = _get_pgsql_command("dropuser", host=host, password=admin_pass, port=port, user=admin_user)
        base.append(name)

        return Command(" ".join(base), **kwargs)
    elif op == "exists":
        kwargs.setdefault("comment", "determine if %s postgres user exits" % name)
        kwargs.setdefault("register", "pgsql_use_exists")

        base = _get_pgsql_command("psql", host=host, password=admin_pass, port=port, user=admin_user)

        sql = "SELECT 1 FROM pgsql_roles WHERE rolname='%s'" % name
        base.append('-c "%s"' % sql)

        return Command(" ".join(base), **kwargs)
    else:
        raise NameError("Unrecognized or unsupported Postgres user operation: %s" % op)


PGSQL_MAPPINGS = {
    'pgsql.create': pgsql_create,
    'pgsql.drop': pgsql_drop,
    'pgsql.dump': pgsql_dump,
    'pgsql.exists': pgsql_exists,
    'pgsql.sql': pgsql_exec,
    'pgsql.user': pgsql_user,
}
