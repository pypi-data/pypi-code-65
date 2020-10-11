# coding=utf-8
""" Output related functions.

Logging and printing support.
"""
import logging
from IPython.core.interactiveshell import InteractiveShell
import IPython.display as ipd

FILENAME = "logfile.log"

LOG_LEVEL = logging.INFO

LOG_FORMAT = (
    "%(asctime)s %(levelname)s [%(threadName)s]"
    " [%(filename)s]%(module)s.%(funcName)s():%(lineno)d %(message)s"
)


def show_all_items():
    """ Show multiple items in output of a cell"""
    InteractiveShell.ast_node_interactivity = "all"


def configure_logging(log_to_file=False):
    """Configure basic logging framework.

    :param log_to_file: True to log to file, False to log on console only.
    """
    if log_to_file:
        logging.basicConfig(filename=FILENAME,
                            format=LOG_FORMAT, level=LOG_LEVEL)
    else:
        logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
    logging.info("Restarting notebook ...")


def print_md(msg, color=None):
    """Print message with Markdown support.

    The message supports markdown syntax like **bold** or _italics_.

    :param msg: message to print.
    :param color: name of desired text color, e.g. 'red'
    """
    color_msg = "<span style='color:{}'>{}</span>".format(color, msg)
    ipd.display(ipd.Markdown(color_msg))


def colorize(msg, color=None):
    """Prepare a sub-msg for printing colorized with print_md()."""
    return "<span style='color:{}'>{}</span>".format(color, msg)


def msg_blue(msg):
    """Prepare blue message."""
    return colorize(msg, color='blue')


def msg_green(msg):
    """Prepare green message."""
    return colorize(msg, color='green')


def msg_red(msg):
    """Prepare red message."""
    return colorize(msg, color='red')


def highlight(msg, color='yellow'):
    """Prepare a sub-msg for printing highlighted with print_md()."""
    return "<span style='background:{}'>{}</span>".format(color, msg)
