import functools

import click
from click_didyoumean import DYMMixin
from click_help_colors import HelpColorsGroup

OPTIONS_FILE_OPTION_NAME = "optionsFile"
OPTIONS_FILE_PARAMETER_NAME = "options_file"
OPTIONS_DUMP_FILE_OPTION_NAME = "createOptionsFile"


class ClickGroup(DYMMixin, HelpColorsGroup):
    pass


def deprecated(msg):
    deprecated_invoke_notice = (
        msg
        + """\nFor more information, please see:

https://docs.taktile.com
If you depend on functionality not listed there, please file an issue."""
    )

    def new_invoke(self, ctx):
        click.echo(click.style(deprecated_invoke_notice, fg="red"), err=True)
        super(type(self), self).invoke(ctx)

    def decorator(f):
        f.invoke = functools.partial(new_invoke, f)

    return decorator
