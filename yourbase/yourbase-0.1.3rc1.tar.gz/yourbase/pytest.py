# This file sets up YourBase pytest integration.
#
# For projects using pytest, the project only needs to add yourbase to its
# requirements file. This file will be run as an entry point (via setup.py) and
# will attach to pytest hooks so that tests do not need to be decorated.
#
# For projects not using pytest, or when running outside of the YourBase CI,
# this file does nothing.

import atexit
import inspect
import os
import yourbase

from typing import List

if yourbase.ENABLED:
    try:
        import pytest

        print("[YB] pytest found, attaching")
        from . import skip_when_possible

        atexit.register(yourbase.shutdown_acceleration, None, None)

        def pytest_collection_modifyitems(items: List[pytest.Item]):
            if yourbase.PLUGIN is None:
                return

            for item in items:
                fname = "%s" % (item.function.__qualname__)
                fpath = os.getcwd() + os.sep + inspect.getfile(item.function)

                if yourbase.PLUGIN.can_skip(fpath, fname):
                    item.add_marker(
                        pytest.mark.skip(reason="[YB] No dependencies changed ✨")
                    )

        def pytest_runtest_setup(item: pytest.Item):
            if yourbase.PLUGIN is None:
                return

            fname = "%s" % (item.function.__qualname__)
            fpath = os.getcwd() + os.sep + inspect.getfile(item.function)

            yourbase.PLUGIN.start_test(fname, fpath)

        def pytest_runtest_teardown(item: pytest.Item):
            if yourbase.PLUGIN is None:
                return

            fname = "%s" % (item.function.__qualname__)
            fpath = os.getcwd() + os.sep + inspect.getfile(item.function)

            yourbase.PLUGIN.end_test(fname, fpath)

    except ModuleNotFoundError:
        print(
            "[YB] YourBase pytest code was initiated, but pytest wasn't found. Is pytest installed oddly?"
        )
