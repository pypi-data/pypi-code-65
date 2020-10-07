import importlib.resources
import locale
import os
from time import sleep

import click
import i18n
from plyer import notification
from plyer.utils import platform
import pyomodoro.resources
import pyomodoro.locale
import yaml


ICON = 'pyomodoro.' + ('ico' if platform == 'win' else 'png')


class CommandWithConfigFile(click.Command):
    """Represents a Click Command that loads values from a config file.

    Attributes:
        config_file_param (string): The name of the config_file param as set on the Click command.
    """
    config_file_param = 'config_file'

    def invoke(self, ctx):
        config_file = ctx.params[self.config_file_param]
        try:
            with open(config_file) as f:
                try:
                    config_data = yaml.safe_load(f)
                except yaml.scanner.ScannerError:
                    raise click.UsageError(i18n.t('error.config_file.scanner_error', config_file=config_file))
                defaults = {param.name: param.get_default(ctx) for param in ctx.command.params}
                # Use the settings from config_file only if the setting is not the default
                # This allows the command line flags to take precedence
                # Ignores the config_file setting to avoid unclear behavior
                for param, value in ctx.params.items():
                    if value is defaults[param] and param in config_data and param is not self.config_file_param:
                        ctx.params[param] = config_data[param]
        except FileNotFoundError:
            # Ignore the exception if config_file is the default value
            # Raise a click exception otherwise, which formats the error and exits cleanly
            for param in ctx.command.params:
                if param.name == self.config_file_param:
                    if ctx.params[self.config_file_param] == param.get_default(ctx):
                        pass
                    else:
                        raise click.BadParameter(i18n.t('error.config_file.not_found', config_file=config_file))
        return super(CommandWithConfigFile, self).invoke(ctx)


def set_locale(loc):
    """Set the locale file to use.

    If the explicit locale shortcode provided does not exist as a locale resource, the first locale resource
    with the same first two characters is selected. If no locale resource matches the first two characters,
    defaults to en_US.

    Args:
        loc: POSIX locale short code
    """
    lang = ''
    if importlib.resources.is_resource(pyomodoro.locale, loc + '.yml'):
        lang = loc
    else:
        loc = loc[:2]
        for r in importlib.resources.contents(pyomodoro.locale):
            for ext in ('.yml', '.yaml'):
                r = r.replace(ext, '')
            if loc == r[:2]:
                lang = r
    return i18n.set('locale', lang or 'en_US')


# i18n.set('enable_memoization', True)
i18n.set('filename_format', '{locale}.{format}')
locale.setlocale(locale.LC_ALL, '')
i18n.load_path.append(os.path.dirname(pyomodoro.locale.__file__))
set_locale(locale.getdefaultlocale()[0])


def pomodoro(task, length):
    """Begin a pomodoro with a notification.

    Args:
        task: Task being focused on. Used as the title in notifications.
        length: Length of the pomodoro in minutes.
    """
    click.echo(i18n.t('pomodoro.message', count=length, task=task, length=length))
    try:
        with importlib.resources.path(pyomodoro.resources, ICON) as icon_path:
            notification.notify(
                title=task,
                message=i18n.t('pomodoro.message', count=length, task=task, length=length),
                app_name='Pyomodoro',
                app_icon=str(icon_path),
            )
        poll_rate = 0.1
        with click.progressbar(range(int(round((length / poll_rate) * 60)))) as bar:
            for _i in bar:
                sleep(poll_rate)
    except UserWarning:
        pass
    except NotImplementedError:
        pass


def take_break(title, message, length):
    """Take a break between pomodoros.

    Args:
        title: The title to use for notifications.
        message: The message to display in notifications.
        length: Length of the break in minutes.
    """
    click.echo(message)
    try:
        with importlib.resources.path(pyomodoro.resources, ICON) as icon_path:
            notification.notify(
                title=title,
                message=message,
                app_name='Pyomodoro',
                app_icon=str(icon_path),
            )
        poll_rate = 0.1
        with click.progressbar(range(int(round((length / poll_rate) * 60)))) as bar:
            for _i in bar:
                sleep(poll_rate)
    except UserWarning:
        pass
    except NotImplementedError:
        pass


def end_break():
    """Send a notification that a break has ended and wait for the user's input."""
    try:
        with importlib.resources.path(pyomodoro.resources, ICON) as icon_path:
            notification.notify(
                title=i18n.t('end_break.title'),
                message=i18n.t('end_break.message'),
                app_name='Pyomodoro',
                app_icon=str(icon_path),
            )
    except UserWarning:
        pass
    except NotImplementedError:
        pass
    return click.confirm(
        i18n.t('end_break.message'),
        default=True,
        show_default=True,
        err=True,
    )


@click.command('start', short_help='Start a Pomodoro Technique session', cls=CommandWithConfigFile)
@click.option('--ask-task', '-t', 'ask_task', envvar='POM_ASK_TASK',
              help='Specify your task for this focusing session', is_flag=True)
@click.option('--config-file', '-f', 'config_file', envvar='POM_CONFIG_FILE',
              default='~/.pyomodoro', help='Path to a Pyomodoro config file', show_default=True)
@click.option('--dry-run', '-d', 'dry_run', help='Print the parsed options and exit', is_flag=True)
@click.option('--language', '-l', 'language', envvar='POM_LANGUAGE',
              help='Override the locale picked up from your system', show_default=True)
@click.option('--long-break-length', '-lb', 'long_break_length', envvar='POM_LONG_BREAK_LENGTH',
              default=20, help='The length of your long breaks in minutes', show_default=True)
@click.option('--pomodoro-length', '-p', 'pomodoro_length', envvar='POM_POMODORO_LENGTH',
              default=25, help='The length of your focusing period in minutes', show_default=True)
@click.option('--short-break-length', '-sb', 'short_break_length', envvar='POM_SHORT_BREAK_LENGTH',
              default=5, help='The length of your short breaks in minutes', show_default=True)
def start(ask_task, config_file, dry_run, language, long_break_length, pomodoro_length, short_break_length):
    """Start a Pomodoro Technique session."""
    # TODO: click's help params don't accept i18n.t() results
    # Find a way to translate the help text

    if language:
        set_locale(language)

    if dry_run:
        click.echo(f'ask_task: {ask_task}')
        click.echo(f'config_file: {config_file}')
        click.echo(f'dry_run: {dry_run}')
        click.echo(f"language: {i18n.get('locale')}")
        click.echo(f'long_break_length: {long_break_length}')
        click.echo(f'pomodoro_length: {pomodoro_length}')
        click.echo(f'short_break_length: {short_break_length}')
        return

    if ask_task:
        task = click.prompt(i18n.t('start.ask_task_prompt')).title()
    else:
        task = i18n.t('start.task_default')

    focusing = True

    while focusing:
        for pomodoros in range(1, 5):
            click.echo(f'Pomodoro #{pomodoros}')
            pomodoro(task, pomodoro_length)
            if pomodoros < 4:
                take_break(
                    i18n.t('take_break.short.title'),
                    i18n.t('take_break.short.message', short_break_length=short_break_length, count=short_break_length),
                    short_break_length
                )
            else:
                take_break(
                    i18n.t('take_break.long.message'),
                    i18n.t('take_break.long.message', long_break_length=long_break_length, count=long_break_length),
                    long_break_length
                )
            focusing = end_break()
            if focusing:
                continue
            else:
                break
