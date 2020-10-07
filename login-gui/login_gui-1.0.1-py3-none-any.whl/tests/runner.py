"""
runner start all test in tests file
"""
import os
import unittest

from HtmlTestRunner import HTMLTestRunner

from login_gui.version import version


def runner():
    """
    run all test of one_suite.
    in kwargs can you append new options.
    """
    one_suite = unittest.defaultTestLoader.discover(".", pattern="test_*.py")
    kwargs = {
        "output": os.path.join(os.path.abspath(os.path.dirname(__file__)), '..\\.log\\test_report\\'),
        "report_name": "login_gui",
        "report_title": "login_gui %s" % version,
        "failfast": False,
        "add_timestamp": False,
        "open_in_browser": False,
        "combine_reports": True
    }
    HTMLTestRunner(**kwargs).run(one_suite)


if __name__ == '__main__':
    runner()
