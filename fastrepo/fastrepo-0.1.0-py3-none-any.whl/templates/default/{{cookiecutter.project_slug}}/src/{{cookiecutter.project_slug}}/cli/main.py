""" Command Line Interface implementation for the {{ cookiecutter.project_slug }} package.

Two flags are available for the command line tool, I.E:

  - version: When version flag is passed (`--version`) the application will print the version and exit successfully.

  - verbose: When verbose flag is passed ( `--verbose`) the application state will be updated and verbose key will be set to True.
             Each command can check if verbose state is enabled and act accordingly.

The list of command can be printed with  {{ cookiecutter.cli_name }} --help.
"""

import typer

from .. import __version__


app = typer.Typer()


state = {"verbose": False}


def version_callback(value: bool) -> None:
    """ Print version and exit when given value is True. """
    if value:
        typer.echo(f"{{ cookiecutter.cli_name }} version: {__version__}")
        raise typer.Exit()


@app.callback()
def base(
    version: bool = typer.Option(
        False, "--version", callback=version_callback, is_eager=True
    ),
    verbose: bool = False,
) -> None:
    """ {{ cookiecutter.project_name }} command line interface. """
    if verbose:
        state["verbose"] = True


@app.command()
def hello(
    name: str = typer.Option(
        default="world", help="The name to greet. If not specified default to 'world'"
    )
):
    """ Say hello to given name. """
    if state["verbose"]:
        typer.echo("DEBUG: Running command 'hello'")
    typer.echo(f"Hello {name}")
