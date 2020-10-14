import click

from fullGSapi.cli.login import login
from fullGSapi.cli.download_commands import download_grades
from fullGSapi.cli.submit import submit
from fullGSapi.cli.utils import get_clients, login_token_path_option

@click.group()
@click.option('--debug/--no-debug', default=False)
@login_token_path_option
@click.pass_context
def cli(ctx: click.Context, debug: bool, tokenpath: str):
    """
    This is the CLI for Gradescope.
    """
    ctx.ensure_object(dict)
    ctx.obj["TOKEN"] = None
    ctx.obj["DEBUG"] = debug

    if not ctx.invoked_subcommand == "login":
        ctx.obj["TOKEN"] = get_clients(ctx, tokenpath)


cli.add_command(login)
cli.add_command(download_grades)
cli.add_command(submit)

if __name__ == '__main__':
    cli()