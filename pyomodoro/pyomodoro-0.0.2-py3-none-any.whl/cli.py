import importlib.resources
from time import sleep
import yaml

import click
from plyer import notification
from plyer.utils import platform
import pyomodoro.resources


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
                    raise click.UsageError(f'failed processing {config_file}')
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
                        raise click.BadParameter(f'{config_file} not found')
        return super(CommandWithConfigFile, self).invoke(ctx)


def pomodoro(task, length):
    """Begin a pomodoro with a notification.

    Args:
        task: Task being focused on. Used as the title in notifications.
        length: Length of the pomodoro in minutes.
    """
    click.echo(
        f'{task} - Focus on your task for {length} minute{"s" if length != 1 else ""}.'
        ' I\'ll ping you when it\'s time for a break.'
    )
    try:
        with importlib.resources.path(pyomodoro.resources, ICON) as icon_path:
            notification.notify(
                title=task,
                message=(f'Focus on your task for {length} minute{"s" if length != 1 else ""}.'
                         ' I\'ll ping you when it\'s time for a break.'),
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
                title='Ready To Continue Focusing?',
                message='Finished with your break and ready to continue focusing?',
                app_name='Pyomodoro',
                app_icon=str(icon_path),
            )
    except UserWarning:
        pass
    except NotImplementedError:
        pass
    return click.confirm(
        'Finished with your break and ready to continue focusing?',
        default=True,
        show_default=True,
        err=True,
    )


@click.command('start', short_help='start a Pomodoro Technique session', cls=CommandWithConfigFile)
@click.option('--config-file', '-f', 'config_file', envvar='POM_CONFIG_FILE', default='~/.pyomodoro', show_default=True)
@click.option('--pomodoro-length', '-p', 'pomodoro_length', envvar='POM_POMODORO_LENGTH', default=25, show_default=True)
@click.option('--short-break-length', '-sb', 'short_break_length', envvar='POM_SHORT_BREAK_LENGTH',
              default=5, show_default=True)
@click.option('--long-break-length', '-lb', 'long_break_length', envvar='POM_LONG_BREAK_LENGTH',
              default=20, show_default=True)
@click.option('--ask-task', '-t', 'ask_task', envvar='POM_ASK_TASK', is_flag=True)
@click.option('--dry-run', '-d', 'dry_run', is_flag=True)
def start(config_file, pomodoro_length, short_break_length, long_break_length, ask_task, dry_run):
    """Start a Pomodoro Technique session."""

    if dry_run:
        click.echo(f'config_file: {config_file}')
        click.echo(f'pomodoro_length: {pomodoro_length}')
        click.echo(f'short_break_length: {short_break_length}')
        click.echo(f'long_break_length: {long_break_length}')
        click.echo(f'ask_task: {ask_task}')
        click.echo(f'dry_run: {dry_run}')
        return

    if ask_task:
        task = click.prompt('My task is to').title()
    else:
        task = 'Focus'

    focusing = True

    while focusing:
        for pomodoros in range(1, 5):
            click.echo(f'Pomodoro #{pomodoros}')
            pomodoro(task, pomodoro_length)
            if pomodoros < 4:
                take_break(
                    'Take A Short Break',
                    (f'Take a short break for {short_break_length} minute{"s" if short_break_length != 1 else ""}.'
                        ' Stand up and stretch, look out a window, or get some water.'),
                    short_break_length
                )
            else:
                take_break(
                    'Take A Long Break',
                    (f'Take a long break for {long_break_length} minute{"s" if long_break_length != 1 else ""}.'
                        ' You\'ve earned it!'),
                    long_break_length
                )
            focusing = end_break()
            if focusing:
                continue
            else:
                break
