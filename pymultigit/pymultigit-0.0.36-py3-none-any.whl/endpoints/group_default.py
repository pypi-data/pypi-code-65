"""
The default group of operations that pymultigit has
"""

from pytconf import register_endpoint, register_function_group

import pymultigit.version
from pymultigit.configs import ConfigDebug, ConfigGrep
from pymultigit.core import do_count, is_dirty, has_untracked_files, non_synchronized_with_upstream, \
    do_for_all_projects, do_clean, do_status, do_dirty, do_build, do_pull, do_grep, do_print

GROUP_NAME_DEFAULT = "default"
GROUP_DESCRIPTION_DEFAULT = "all pymultigit commands"


def register_group_default():
    """
    register the name and description of this group
    """
    register_function_group(
        function_group_name=GROUP_NAME_DEFAULT,
        function_group_description=GROUP_DESCRIPTION_DEFAULT,
    )


@register_endpoint(
    configs=[
        ConfigDebug,
    ],
    group=GROUP_NAME_DEFAULT,
)
def version() -> None:
    """
    Print version
    """
    print(pymultigit.version.VERSION_STR)


@register_endpoint(
    configs=[
        ConfigDebug,
    ],
    group=GROUP_NAME_DEFAULT,
)
def dirty() -> None:
    """ show the status of multiple git repositories """
    do_count(is_dirty, 'is dirty', 'is clean', 'were dirty')


@register_endpoint(
    configs=[
        ConfigDebug,
    ],
    group=GROUP_NAME_DEFAULT,
)
def untracked() -> None:
    """ show which repositories have untracked files """
    do_count(has_untracked_files, 'has untracked files', 'is fully tracked', 'have untracked files')


@register_endpoint(
    configs=[
        ConfigDebug,
    ],
    group=GROUP_NAME_DEFAULT,
)
def synchronized() -> None:
    """ show which repositories are synchronized with their upstream """
    do_count(non_synchronized_with_upstream, 'is behind upstream', 'is synchronized', 'are behind upstream')


@register_endpoint(
    configs=[
        ConfigDebug,
    ],
    group=GROUP_NAME_DEFAULT,
)
def clean() -> None:
    """ clean all projects """
    do_for_all_projects(do_clean)


@register_endpoint(
    configs=[
        ConfigDebug,
    ],
    group=GROUP_NAME_DEFAULT,
)
def status() -> None:
    """ show the status of multiple git repositories """
    do_for_all_projects(do_status)


@register_endpoint(
    configs=[
        ConfigDebug,
    ],
    group=GROUP_NAME_DEFAULT,
)
def dirty() -> None:
    """ show names of project which are dirty """
    do_for_all_projects(do_dirty)


@register_endpoint(
    configs=[
        ConfigDebug,
    ],
    group=GROUP_NAME_DEFAULT,
)
def build() -> None:
    """ build multiple git repositories """
    do_for_all_projects(do_build)


@register_endpoint(
    configs=[
        ConfigDebug,
    ],
    group=GROUP_NAME_DEFAULT,
)
def pull() -> None:
    """ pull changes for multiple git repositories """
    do_for_all_projects(do_pull)


@register_endpoint(
    configs=[
        ConfigDebug,
        ConfigGrep,
    ],
    group=GROUP_NAME_DEFAULT,
)
def grep() -> None:
    """ grep multiple repositories for pattern """
    do_for_all_projects(do_grep)


@register_endpoint(
    configs=[
        ConfigDebug,
    ],
    group=GROUP_NAME_DEFAULT,
)
def list_projects() -> None:
    """ list all projects """
    do_for_all_projects(do_print)
