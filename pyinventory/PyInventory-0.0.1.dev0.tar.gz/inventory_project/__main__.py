"""
    Helper to call django manage commands
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    used in
    for, e.g.:

    ~/DjangoInventoryEnv/bin/python3 -m inventory_project --help
"""
import os
import sys

from django.core.management import execute_from_command_line
from django_tools.exception_plus import print_exc_plus


def manage():
    os.environ["DJANGO_SETTINGS_MODULE"] = "inventory_project.settings"
    try:
        execute_from_command_line(sys.argv)
    except SystemExit as err:
        sys.exit(err.code)
    except BaseException:
        print_exc_plus()
        sys.exit(-1)


if __name__ == "__main__":
    manage()
