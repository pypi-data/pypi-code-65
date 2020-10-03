"""
main
"""
import pylogconf.core
from pytconf import register_endpoint, register_main, config_arg_parse_and_launch

from pypathutil import common
from pypathutil.configs import ConfigFolder, ConfigPath, ConfigHead, ConfigSeparator, ConfigOps
from pypathutil.static import DESCRIPTION, APP_NAME, VERSION_STR


@register_endpoint(
    configs=[
        ConfigFolder,
        ConfigPath,
        ConfigHead,
        ConfigSeparator,
        ConfigOps,
    ],
    description="Add two paths together",
)
def add() -> None:
    new_path = common.add(
        path=ConfigPath.path,
        folder=ConfigFolder.folder,
        head=ConfigHead.head,
        separator=ConfigSeparator.separator,
        remove_duplicates=ConfigOps.remove_duplicates,
        remove_non_folders=ConfigOps.remove_non_folders,
        remove_non_abs=ConfigOps.remove_non_abs,
    )
    print(new_path)


@register_endpoint(
    configs=[
        ConfigSeparator,
        ConfigOps,
        ConfigPath,
    ],
    description="Clean a path, removing elements which repeat or are not valid paths",
)
def clean() -> None:
    path = common.clean(
        path=ConfigPath.path,
        separator=ConfigSeparator.separator,
        remove_duplicates=ConfigOps.remove_duplicates,
        remove_non_folders=ConfigOps.remove_non_folders,
        remove_non_abs=ConfigOps.remove_non_abs,
    )
    print(path)


@register_endpoint(
    configs=[
        ConfigOps,
        ConfigSeparator,
        ConfigPath,
        ConfigFolder,
    ],
    description="Remove element from a path",
)
def remove() -> None:
    new_path = common.remove(
        path=ConfigPath.path,
        folder=ConfigFolder.folder,
        separator=ConfigSeparator.separator,
        remove_duplicates=ConfigOps.remove_duplicates,
        remove_non_folders=ConfigOps.remove_non_folders,
        remove_non_abs=ConfigOps.remove_non_abs,
    )
    print(new_path)


@register_main(
    main_description=DESCRIPTION,
    app_name=APP_NAME,
    version=VERSION_STR,
)
def main():
    pylogconf.core.setup()
    config_arg_parse_and_launch()


if __name__ == '__main__':
    main()
