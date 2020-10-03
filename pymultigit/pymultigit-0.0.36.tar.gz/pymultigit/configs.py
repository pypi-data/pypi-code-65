"""
All configurations for pymultigit
"""


from pytconf import Config, ParamCreator


class ConfigDebug(Config):
    """
    Parameters for debug
    """
    verbose = ParamCreator.create_bool(
        help_string="be verbose?",
        default=False,
    )
    git_verbose = ParamCreator.create_bool(
        help_string="add --verbose when running git?",
        default=False,
    )
    terse = ParamCreator.create_bool(
        help_string="be terse?",
        default=False,
    )
    quiet = ParamCreator.create_bool(
        help_string="be quiet?",
        default=False,
    )
    git_quiet = ParamCreator.create_bool(
        help_string="add --quiet when running git?",
        default=False,
    )
    stats = ParamCreator.create_bool(
        help_string="show statistics are the end?",
        default=False,
    )
    sort = ParamCreator.create_bool(
        help_string="sort results by project name?",
        default=True,
    )


class ConfigGrep(Config):
    """
    Parameters for pymultigit
    """

    regexp = ParamCreator.create_str(
        help_string="what regexp to look for?",
    )
