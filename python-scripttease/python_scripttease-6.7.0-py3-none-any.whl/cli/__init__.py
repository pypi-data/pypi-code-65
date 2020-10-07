# Imports

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from commonkit.logging import LoggingHelper
from ..constants import LOGGER_NAME
from ..version import DATE as VERSION_DATE, VERSION
from . import initialize
from . import subcommands

DEBUG = 10

logging = LoggingHelper(colorize=True, name=LOGGER_NAME)
log = logging.setup()

# Commands


def main_command():
    """Process script configurations."""

    __author__ = "Shawn Davis <shawn@develmaycare.com>"
    __date__ = VERSION_DATE
    __help__ = """NOTES

This command is used to parse configuration files and output the commands.

    """
    __version__ = VERSION

    # Main argument parser from which sub-commands are created.
    parser = ArgumentParser(description=__doc__, epilog=__help__, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument(
        "path",
        default="commands.ini",
        nargs="?",
        help="The path to the configuration file."
    )

    parser.add_argument(
        "-c",
        "--color",
        action="store_true",
        dest="color_enabled",
        help="Enable code highlighting for terminal output."
    )

    parser.add_argument(
        "-C=",
        "--context=",
        action="append",
        dest="variables",
        help="Context variables for use in pre-parsing the config and templates. In the form of: name:value"
    )

    parser.add_argument(
        "-d",
        "--docs",
        action="store_true",
        dest="docs_enabled",
        help="Output documentation instead of code."
    )

    # parser.add_argument(
    #     "-d=",
    #     "--docs=",
    #     choices=["html", "markdown", "plain", "rst"],
    #     dest="docs_enabled",
    #     help="Output documentation instead of code."
    # )

    parser.add_argument(
        "-D",
        "--debug",
        action="store_true",
        dest="debug_enabled",
        help="Enable debug output."
    )

    parser.add_argument(
        "-f=",
        "--filter=",
        action="append",
        dest="filters",
        help="Filter the commands in the form of: attribute:value"
    )

    parser.add_argument(
        "-O=",
        "--option=",
        action="append",
        dest="options",
        help="Common command options in the form of: name:value"
    )

    # parser.add_argument(
    #     "-O=",
    #     "--output=",
    #     # default=os.path.join("prototype", "output"),
    #     dest="output_path",
    #     help="Output to the given directory. Defaults to ./prototype/output/"
    # )

    parser.add_argument(
        "-s",
        "--script",
        action="store_true",
        dest="script_enabled",
        help="Output commands as a script."
    )

    parser.add_argument(
        "-T=",
        "--template-path=",
        action="append",
        dest="template_locations",
        help="The location of template files that may be used with the template command."
    )

    parser.add_argument(
        "-w=",
        "--write=",
        dest="output_file",
        help="Write the output to disk."
    )

    parser.add_argument(
        "-V=",
        "--variables-file=",
        dest="variables_file",
        help="Load variables from a file."
    )

    # Access to the version number requires special consideration, especially
    # when using sub parsers. The Python 3.3 behavior is different. See this
    # answer: http://stackoverflow.com/questions/8521612/argparse-optional-subparser-for-version
    parser.add_argument(
        "-v",
        action="version",
        help="Show version number and exit.",
        version=__version__
    )

    parser.add_argument(
        "--version",
        action="version",
        help="Show verbose version information and exit.",
        version="%(prog)s" + " %s %s by %s" % (__version__, __date__, __author__)
    )

    # Parse arguments.
    args = parser.parse_args()

    if args.debug_enabled:
        log.setLevel(DEBUG)

    log.debug("Namespace: %s" % args)

    # Load context.
    context = dict()
    if args.variables:
        context = initialize.context_from_cli(args.variables)

    # Load additional context from file.
    if args.variables_file:
        variables = initialize.variables_from_file(args.variables_file)
        if variables:
            context.update(variables)

    # Handle filters.
    filters = None
    if args.filters:
        filters = initialize.filters_from_cli(args.filters)

    # Handle options.
    options = None
    if args.options:
        options = initialize.options_from_cli(args.options)

    # Process the request.
    if args.docs_enabled:
        exit_code = subcommands.output_docs(
            args.path,
            context=context,
            filters=filters,
            locations=args.template_locations,
            options=options
        )
    elif args.script_enabled:
        exit_code = subcommands.output_script(
            args.path,
            color_enabled=args.color_enabled,
            context=context,
            locations=args.template_locations,
            options=options
        )
    else:
        exit_code = subcommands.output_commands(
            args.path,
            color_enabled=args.color_enabled,
            context=context,
            filters=filters,
            locations=args.template_locations,
            options=options
        )

    exit(exit_code)
