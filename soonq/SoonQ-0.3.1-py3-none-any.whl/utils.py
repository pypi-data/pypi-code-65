"""Utility functionalities.

Functions:
echo
"""

import functools

try:
    import click
    feedback_func = click.echo
except ModuleNotFoundError:
    feedback_func = print


@functools.wraps(feedback_func)
def echo(*args, **kwargs):
    """Function for giving feedback. Tries to use click.echo, but
    defaults to print if Click is not installed.
    """
    return feedback_func(*args, **kwargs)
