# Imports

from commonkit import highlight_code
from commonkit.shell import EXIT
from ..parsers import load_commands, load_config

# Exports

__all__ = (
    "output_commands",
    "output_docs",
    "output_script",
)

# Functions


def output_commands(path, color_enabled=False, context=None, filters=None, locations=None, options=None):
    """Output commands found in a given configuration file.

    :param path: The path to the configuration file.
    :type path: str

    :param color_enabled: Indicates the output should be colorized.
    :type color_enabled: bool

    :param context: The context to be applied to the file before parsing it as configuration.
    :type context: dict

    :param filters: Output only those commands which match the given filters.
    :type filters: dict

    :param locations: The locations (paths) of additional resources.
    :type locations: list[str]

    :param options: Options to be applied to all commands.
    :type options: dict

    :rtype: int
    :returns: An exit code.

    """
    commands = load_commands(
        path,
        context=context,
        filters=filters,
        locations=locations,
        options=options
    )
    if commands is None:
        return EXIT.ERROR

    output = list()
    for command in commands:
        statement = command.get_statement(cd=True)
        if statement is None:
            continue

        output.append(statement)
        output.append("")

    if color_enabled:
        print(highlight_code("\n".join(output), language="bash"))
    else:
        print("\n".join(output))

    return EXIT.OK


def output_docs(path, context=None, filters=None, locations=None, options=None):
    """Output documentation for commands found in a given configuration file.

    :param path: The path to the configuration file.
    :type path: str

    :param context: The context to be applied to the file before parsing it as configuration.
    :type context: dict

    :param filters: Output only those commands which match the given filters.
    :type filters: dict

    :param locations: The locations (paths) of additional resources.
    :type locations: list[str]

    :param options: Options to be applied to all commands.
    :type options: dict

    :rtype: int
    :returns: An exit code.

    """
    commands = load_commands(
        path,
        context=context,
        filters=filters,
        locations=locations,
        options=options
    )
    if commands is None:
        return EXIT.ERROR

    count = 1
    output = list()
    for command in commands:
        output.append("%s. %s" % (count, command.comment))
        count += 1

    print("\n".join(output))

    return EXIT.OK


def output_script(path, color_enabled=False, context=None, filters=None, locations=None, options=None):
    """Output a script of commands found in a given configuration file.

    :param path: The path to the configuration file.
    :type path: str

    :param color_enabled: Indicates the output should be colorized.
    :type color_enabled: bool

    :param context: The context to be applied to the file before parsing it as configuration.
    :type context: dict

    :param filters: Output only those commands which match the given filters. NOT IMPLEMENTED.
    :type filters: dict

    :param locations: The locations (paths) of additional resources.
    :type locations: list[str]

    :param options: Options to be applied to all commands.
    :type options: dict

    :rtype: int
    :returns: An exit code.

    """
    config = load_config(
        path,
        context=context,
        locations=locations,
        options=options
    )
    if config is None:
        return EXIT.ERROR

    script = config.as_script()
    if color_enabled:
        print(highlight_code(script.to_string(), language="bash"))
    else:
        print(script)

    return EXIT.OK
