import argparse
import textwrap
from typing import List

from convo import telemetry
from convo.cli import SubParsersAction
import convo.cli.utils
from convo.shared.constants import DOCS_URL_TELEMETRY
import convo.shared.utils.cli


def add_subparser(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser],
) -> None:
    """Add all telemetry tracking parsers.

    Args:
        subparsers: subparser we are going to attach to
        parents: Parent parsers, needed to ensure tree structure in argparse
    """

    telemetry_parser = subparsers.add_parser(
        "telemetry",
        parents=parents,
        help="Configuration of Convo Open Source telemetry reporting.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    telemetry_subparsers = telemetry_parser.add_subparsers()
    telemetry_disable_parser = telemetry_subparsers.add_parser(
        "disable",
        parents=parents,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Disable Convo Open Source Telemetry reporting.",
    )
    telemetry_disable_parser.set_defaults(func=disable_telemetry)

    telemetry_enable_parser = telemetry_subparsers.add_parser(
        "enable",
        parents=parents,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Enable Convo Open Source Telemetry reporting.",
    )
    telemetry_enable_parser.set_defaults(func=enable_telemetry)
    telemetry_parser.set_defaults(func=inform_about_telemetry)


def inform_about_telemetry(_: argparse.Namespace) -> None:
    """Inform user about telemetry tracking."""
    is_enabled = telemetry.is_telemetry_enabled()
    if is_enabled:
        convo.shared.utils.cli.print_success(
            "Telemetry reporting is currently enabled for this installation."
        )
    else:
        convo.shared.utils.cli.print_success(
            "Telemetry reporting is currently disabled for this installation."
        )

    print(
        textwrap.dedent(
            """
            Convo uses telemetry to report anonymous usage information. This information
            is essential to help improve Convo Open Source for all users."""
        )
    )

    if not is_enabled:
        print("\nYou can enable telemetry reporting using")
        convo.shared.utils.cli.print_info("\n\tconvo telemetry enable")
    else:
        print("\nYou can disable telemetry reporting using:")
        convo.shared.utils.cli.print_info("\n\tconvo telemetry disable")

    convo.shared.utils.cli.print_success(
        "\nYou can find more information about telemetry reporting at "
        "" + DOCS_URL_TELEMETRY
    )


def disable_telemetry(_: argparse.Namespace) -> None:
    """Disable telemetry tracking."""
    telemetry.track_telemetry_disabled()
    telemetry.toggle_telemetry_reporting(is_enabled=False)
    convo.shared.utils.cli.print_success("Disabled telemetry reporting.")


def enable_telemetry(_: argparse.Namespace) -> None:
    """Enable telemetry tracking."""
    telemetry.toggle_telemetry_reporting(is_enabled=True)
    convo.shared.utils.cli.print_success("Enabled telemetry reporting.")
