# Imports

from ..commands import Command

# Exports

__all__ = (
    "COMMON_MAPPINGS",
    "python_pip",
    "python_virtualenv",
    "run",
    "slack",
    "twist",
    "udf",
)

# Functions


def python_pip(name, op="install", upgrade=False, venv=None, version=3, **kwargs):
    """Use pip to install or uninstall a Python package.

    - name (str): The name of the package.
    - op (str): The operation to perform; install, uninstall
    - upgrade (bool): Upgrade an installed package.
    - venv (str): The name of the virtual environment to load.
    - version (int): The Python version to use, e.g. ``2`` or ``3``.

    """
    manager = "pip"
    if version == 3:
        manager = "pip3"

    if upgrade:
        statement = "%s install --upgrade %s" % (manager, name)
    else:
        statement = "%s %s %s" % (manager, op, name)

    if venv is not None:
        kwargs['prefix'] = "source %s/bin/activate" % venv

    kwargs.setdefault("comment", "%s %s" % (op, name))

    return Command(statement, **kwargs)


def python_virtualenv(name, **kwargs):
    """Create a Python virtual environment.

    - name (str): The name of the environment to create.

    """
    kwargs.setdefault("comment", "create %s virtual environment" % name)

    return Command("virtualenv %s" % name, **kwargs)


def run(statement, **kwargs):
    """Run any statement.

    - statement (str): The statement to be executed.

    """
    kwargs.setdefault("comment", "run statement")
    return Command(statement, **kwargs)


def slack(message, url=None, **kwargs):
    """Send a message to Slack.

    - message (str): The message to be sent.
    - url (str): The webhook URL. This is required. See documentation.

    """
    if url is None:
        raise ValueError("A url is required to use the slack command.")

    kwargs.setdefault("comment", "send a message to slack")

    a = list()

    a.append("curl -X POST -H 'Content-type: application/json' --data")
    a.append("'" + '{"text": "%s"}' % message + "'")
    a.append(url)

    return Command(" ".join(a), **kwargs)


def twist(message, title="Notice", url=None, **kwargs):
    """Send a message to Twist.

    - message (str): The message to be sent.
    - title (str): The message title.
    - url (str): The webhook URL. This is required. See documentation.

    """
    if url is None:
        raise ValueError("A url is required to use the twist command.")

    kwargs.setdefault("comment", "send a message to twist")

    a = list()

    # curl -X POST -H 'Content-type: application/json' --data '{"content": "This is the message.", "title": "Message Title"}' "https://twist.com/api/v3/integration_incoming/post_data?install_id=116240&install_token=116240_bfb05bde51ecd0f728b4b161bee6fcee"
    a.append("curl -X POST -H 'Content-type: application/json' --data")

    data = '{"content": "%s", "title": "%s"}' % (message, title)
    a.append("'%s'" % data)
    a.append('"%s"' % url)

    return Command(" ".join(a), **kwargs)


def udf(name, default=None, example=None, label=None, **kwargs):
    """Create a UDF prompt for a StackScript.

    - name (str): The name of the variable.
    - default: The default value.
    - example: An example value, instead of a default.
    - label (str): The label for the variable.

    """
    kwargs.setdefault("prompt for %s in stackscript" % name)

    label = label or name.replace("_", " ").title()

    a = ['# <UDF name="%s" label="%s"' % (name, label)]

    if default is not None:
        a.append('default="%s"' % default)
    elif example is not None:
        a.append('example="%s"' % example)
    else:
        pass

    a.append("/>")

    return Command(" ".join(a), **kwargs)


# Mappings

COMMON_MAPPINGS = {
    'pip': python_pip,
    'run': run,
    'slack': slack,
    'twist': twist,
    'udf': udf,
    'virtualenv': python_virtualenv,
}
