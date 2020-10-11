from stdiomask import getpass
import inquirer
import click


def option_selector(msg, options):
    answer = inquirer.prompt([
        inquirer.List('value', message=msg, choices=options)
    ])
    if answer is None:
        raise click.Abort()
    return answer.get("value")


def checkboxes(msg, options):
    msg += " (use space to check an option, enter to submit)"
    answer = inquirer.prompt([
        inquirer.Checkbox('value', message=msg, choices=options)
    ])

    if answer is None:
        raise click.Abort()
    return answer.get("value")


def text(msg, validate=None):
    if validate is not None:
        value = inquirer.Text('value', message=msg, validate=validate)
    else:
        value = inquirer.Text('value', message=msg)
    answer = inquirer.prompt([value])

    if answer is None:
        raise click.Abort()
    return answer.get("value")


def long_text(msg):
    answer = inquirer.prompt([
        inquirer.Editor('value', message=msg)
    ])

    if answer is None:
        raise click.Abort()
    return answer.get("value")


def path(msg, validator="directory", exists=True):
    if validator == "file":
        validator = inquirer.Path.FILE
    else:
        validator = inquirer.Path.DIRECTORY

    answer = inquirer.prompt([
        inquirer.Path('value', message=msg, path_type=validator, exists=exists)
    ])

    if answer is None:
        raise click.Abort()
    return answer.get("value")


def hidden(msg):
    click.echo('[', nl=False)
    click.echo(click.style("?", fg="yellow"), nl=False)
    click.echo('] ', nl=False)
    return getpass(msg+": ")


def confirm(msg, default=True):
    answer = inquirer.prompt({
        inquirer.Confirm('value', message=msg, default=default),
    })

    if answer is None:
        raise click.Abort()
    return answer.get("value")
