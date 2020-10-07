# Imports

import os
from ..commands import Command

# Exports

__all__ = (
    "DJANGO_MAPPINGS",
    "django",
    "django_check",
    "django_collect_static",
    "django_dumpdata",
    "django_loaddata",
    "django_migrate",
)

# Functions


def _django(name, *args, venv=None, **kwargs):
    """Process a django-based command.

    :param name: The name of the management command.
    :type name: str

    :param venv: The virtual environment to use.
    :type venv: str

    args and kwargs are used to instantiate the command instance.

    This exists because we need ``django()`` to serve as an interface for any management command.

    """
    if venv is not None:
        kwargs['prefix'] = "source %s/bin/activate" % venv

    kwargs.setdefault("comment", "run %s django management command" % name)

    # Base parameters need to be captured, because all others are assumed to be switches for the management command.
    _kwargs = {
        'comment': kwargs.pop("comment", None),
        'condition': kwargs.pop("condition", None),
        'cd': kwargs.pop("cd", None),
        'environments': kwargs.pop("environments", None),
        'function': kwargs.pop("function", None),
        # 'local': kwargs.pop("local", False),
        'prefix': kwargs.pop("prefix", None),
        'register': kwargs.pop("register", None),
        'shell': kwargs.pop("shell", "/bin/bash"),
        'stop': kwargs.pop("stop", False),
        'sudo': kwargs.pop('sudo', False),
        'tags': kwargs.pop("tags", None),
    }

    statement = list()
    statement.append("./manage.py %s" % name)

    # Remaining kwargs are assumed to be switches.
    for key, value in kwargs.items():
        key = key.replace("_", "-")
        if type(value) is bool:
            if value is True:
                statement.append("--%s" % key)
        else:
            statement.append("--%s=%s" % (key, value))

    if len(args) > 0:
        statement.append(" ".join(args))

    return Command(" ".join(statement), **_kwargs)


def django(name, *args, venv=None, **kwargs):
    """Run any Django management command.

    - name (str): The name of the management command.
    - venv (str): The of the virtual environment to use.

    args are passed as positional arguments, while kwargs are given as switches.

    """
    if name == "check":
        return django_check(venv=venv, **kwargs)
    elif name in ("collectstatic", "static"):
        return django_collect_static(venv=venv, **kwargs)
    elif name == "migrate":
        return django_migrate(venv=venv, **kwargs)
    else:
        return _django(name, *args, venv=venv, **kwargs)


def django_check(venv=None, **kwargs):
    """Run the Django check command.

    - venv (str): The of the virtual environment to use.

    """
    kwargs.setdefault("comment", "run django checks")
    kwargs.setdefault("register", "django_checks_out")

    return _django("check", venv=venv, **kwargs)


def django_collect_static(venv=None, **kwargs):
    """Collect static files.

    - venv (str): The of the virtual environment to use.

    """
    kwargs.setdefault("comment", "collect static files")

    return _django("collectstatic", venv=venv, **kwargs)


def django_dumpdata(app_name, base_path="local", file_name="initial", indent=4, natural_foreign=False,
                    natural_primary=False, path=None, venv=None, **kwargs):
    """Dump data from the database.

    - app_name (str): The name (app label) of the app. ``app_label.ModelName`` may also be given.
    - base_path (str): The path under which apps are located in source.
    - file_name (str): The file name to which the data will be dumped.
    - indent (int): Indentation of the exported fixtures.
    - natural_foreign (bool): Use the natural foreign parameter.
    - natural_primary (bool): Use the natural primary parameter.
    - path (str): The path to the data file.
    - venv (str): The of the virtual environment to use.

    """
    kwargs.setdefault("comment", "export fixtures for %s" % app_name)

    output_format = kwargs.pop("format", "json")

    _path = path or os.path.join(base_path, app_name, "fixtures", "%s.%s" % (file_name, output_format))

    return _django(
        "dumpdata",
        app_name,
        "> %s" % _path,
        format=output_format,
        indent=indent,
        natural_foreign=natural_foreign,
        natural_primary=natural_primary,
        venv=venv,
        **kwargs
    )


def django_loaddata(app_name, base_path="local", file_name="initial", path=None, venv=None, **kwargs):
    """Load data into the database.

    - app_name (str): The name (app label) of the app. ``app_label.ModelName`` may also be given.
    - base_path (str): The path under which apps are located in source.
    - file_name (str): The file name to which the data will be dumped.
    - path (str): The path to the data file.
    - venv (str): The of the virtual environment to use.

    """
    kwargs.setdefault("comment", "load fixtures for %s" % app_name)

    output_format = kwargs.pop("format", "json")

    _path = path or os.path.join(base_path, app_name, "fixtures", "%s.%s" % (file_name, output_format))

    return _django("loaddata", _path, venv=venv, **kwargs)


def django_migrate(venv=None, **kwargs):
    """Apply database migrations.

    - venv (str): The of the virtual environment to use.

    """
    kwargs.setdefault("comment", "run django database migrations")

    return _django("migrate", venv=venv, **kwargs)

# Mapping


DJANGO_MAPPINGS = {
    'django': django,
    'django.check': django_check,
    'django.collect_static': django_collect_static,
    'django.dumpdata': django_dumpdata,
    'django.loaddata': django_loaddata,
    'django.migrate': django_migrate,
}
