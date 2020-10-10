"""Console script for fcust."""
import click
from pathlib import PosixPath
from fcust.fcust import CommonFolder


@click.command()
@click.argument("folder_path")
def main(
    folder_path: str,
    help="Path where the common foler is located",
):
    fpath = PosixPath(folder_path)
    if not fpath.exists():
        raise FileNotFoundError(f"Specified folder {folder_path} does not exist!")

        # assume common folder itself has been created with proper group and permissions.
    click.echo(f"Initiating maintenance on {folder_path}")
    cf = CommonFolder(folder_path=fpath)
    cf.enforce_permissions()
    click.echo("Common folder maintenance completed.")
