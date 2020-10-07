# Imports

from commonkit import split_csv
from ..commands import Command, Template
from .common import COMMON_MAPPINGS
from .django import DJANGO_MAPPINGS
from .mysql import MYSQL_MAPPINGS
from .pgsql import PGSQL_MAPPINGS
from .posix import POSIX_MAPPINGS, Function

# Exports

__all__ = (
    "MAPPINGS",
    "apache",
    "apache_reload",
    "apache_restart",
    "apache_start",
    "apache_stop",
    "apache_test",
    "command_exists",
    "service_reload",
    "service_restart",
    "service_start",
    "service_stop",
    "system",
    "system_install",
    "system_reboot",
    "system_update",
    "system_upgrade",
    "system_uninstall",
    "template",
    "user",
    "Function",
)


def command_exists(name):
    """Indicates whether a given command exists in this overaly.

    :param name: The name of the command.
    :type name: str

    :rtype: bool

    """
    return name in MAPPINGS


def apache(op, **kwargs):
    """Execute an Apache-related command.

    - op (str): The operation to perform; reload, restart, start, stop, test.

    """
    if op == "reload":
        return apache_reload(**kwargs)
    elif op == "restart":
        return apache_restart(**kwargs)
    elif op == "start":
        return apache_start(**kwargs)
    elif op == "stop":
        return apache_stop(**kwargs)
    elif op == "test":
        return apache_test(**kwargs)
    else:
        raise NameError("Unrecognized or unsupported apache operation: %s" % op)


def apache_reload(**kwargs):
    kwargs.setdefault("comment", "reload apache")
    kwargs.setdefault("register", "apache_reloaded")

    return Command("apachectl –k reload", **kwargs)


def apache_restart(**kwargs):
    kwargs.setdefault("comment", "restart apache")
    kwargs.setdefault("register", "apache_restarted")

    return Command("apachectl –k restart", **kwargs)


def apache_start(**kwargs):
    kwargs.setdefault("comment", "start apache")
    kwargs.setdefault("register", "apache_started")

    return Command("apachectl –k start", **kwargs)


def apache_stop(**kwargs):
    kwargs.setdefault("comment", "stop apache")

    return Command("apachectl –k stop", **kwargs)


def apache_test(**kwargs):
    kwargs.setdefault("comment", "check apache configuration")
    kwargs.setdefault("register", "apache_checks_out")

    return Command("apachectl configtest", **kwargs)


def service_reload(name, **kwargs):
    """Reload a service.

    - name (str): The service name.

    """
    kwargs.setdefault("comment", "reload %s service" % name)
    kwargs.setdefault("register", "%s_reloaded" % name)

    return Command("systemctl reload %s" % name, **kwargs)


def service_restart(name, **kwargs):
    """Restart a service.

    - name (str): The service name.

    """
    kwargs.setdefault("comment", "restart %s service" % name)
    kwargs.setdefault("register", "%s_restarted" % name)

    return Command("ssystemctl restart %s" % name, **kwargs)


def service_start(name, **kwargs):
    """Start a service.

    - name (str): The service name.

    """
    kwargs.setdefault("comment", "start %s service" % name)
    kwargs.setdefault("register", "%s_started" % name)

    return Command("systemctl start %s" % name, **kwargs)


def service_stop(name, **kwargs):
    """Stop a service.

    - name (str): The service name.

    """
    kwargs.setdefault("comment", "stop %s service" % name)
    kwargs.setdefault("register", "%s_stopped" % name)

    return Command("systemctl stop %s" % name, **kwargs)


def system(op, **kwargs):
    """Perform a system operation.

    - op (str): The operation to perform; reboot, update, upgrade.

    """
    if op == "reboot":
        return system_reboot(**kwargs)
    elif op == "update":
        return system_update(**kwargs)
    elif op == "upgrade":
        return system_upgrade(**kwargs)
    else:
        raise NameError("Unrecognized or unsupported system operation: %s" % op)


def system_install(name, **kwargs):
    """Install a system-level package.

    - name (str): The name of the package to install.

    """
    kwargs.setdefault("comment", "install system package %s" % name)

    return Command("yum install -y %s" % name, **kwargs)


def system_reboot(**kwargs):
    kwargs.setdefault("comment", "reboot the system")

    return Command("reboot", **kwargs)


def system_uninstall(name, **kwargs):
    """Uninstall a system-level package.

    - name (str): The name of the package to uninstall.

    """
    kwargs.setdefault("comment", "remove system package %s" % name)

    return Command("yum remove -y %s" % name, **kwargs)


def system_update(**kwargs):
    kwargs.setdefault("comment", "update system package info")

    return Command("yum check-update", **kwargs)


def system_upgrade(**kwargs):
    kwargs.setdefault("comment", "upgrade the system")

    return Command("yum update -y", **kwargs)


def template(source, target, backup=True, parser=None, **kwargs):
    """Create a file from a template.

    - source (str): The path to the template file.
    - target (str): The path to where the new file should be created.
    - backup (bool): Indicates whether a backup should be made if the target file already exists.
    - parser (str): The parser to use ``jinja`` (the default) or ``simple``.

    """
    return Template(source, target, backup=backup, parser=parser, **kwargs)


def user(name, groups=None, home=None, op="add", password=None, **kwargs):
    """Create or remove a user.

    - name (str): The user name.
    - groups (str | list): A list of groups to which the user should belong.
    - home (str): The path to the user's home directory.
    - op (str); The operation to perform; ``add`` or ``remove``.
    - password (str): The user's password. (NOT IMPLEMENTED)

    """
    if op == "add":
        kwargs.setdefault("comment", "create a user named %s" % name)

        commands = list()

        a = list()
        a.append('adduser %s' % name)
        if home is not None:
            a.append("--home %s" % home)

        commands.append(Command(" ".join(a), **kwargs))

        if type(groups) is str:
            groups = split_csv(groups, smart=False)

        if type(groups) in [list, tuple]:
            for group in groups:
                commands.append(Command("gpasswd -a %s %s" % (name, group), **kwargs))

        a = list()
        for c in commands:
            a.append(c.get_statement(suppress_comment=True))

        return Command("\n".join(a), **kwargs)
    elif op == "remove":
        kwargs.setdefault("comment", "remove a user named %s" % name)
        return Command("userdel -r %s" % name, **kwargs)
    else:
        raise NameError("Unsupported or unrecognized operation: %s" % op)


MAPPINGS = {
    'apache': apache,
    'install': system_install,
    'reboot': system_reboot,
    'reload': service_reload,
    'restart': service_restart,
    'start': service_start,
    'stop': service_stop,
    'system': system,
    'template': template,
    'update': system_update,
    'uninstall': system_uninstall,
    'upgrade': system_upgrade,
    'user': user,
}

MAPPINGS.update(COMMON_MAPPINGS)
MAPPINGS.update(DJANGO_MAPPINGS)
MAPPINGS.update(MYSQL_MAPPINGS)
MAPPINGS.update(PGSQL_MAPPINGS)
MAPPINGS.update(POSIX_MAPPINGS)
