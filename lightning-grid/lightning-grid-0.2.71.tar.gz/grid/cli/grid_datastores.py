import click
from typing import Optional
from grid import Grid
from grid.cli.grid_train import get_credentials


@click.command()
@click.option('--source_dir',
              type=click.Path(exists=True, file_okay=True, dir_okay=True),
              required=True,
              help='Source directory to upload datastore files')
@click.option('--name', type=str, required=True, help='Name of the datastore')
@click.option('--grid_credential',
              type=str,
              required=False,
              help='Grid credential ID')
@click.option('--version',
              type=str,
              required=True,
              help='Version of the datastore')
@click.option(
    '--staging_dir',
    type=str,
    default="",
    required=False,
    help='Staging directory to hold the temporary compressed datastore')
def datastores(source_dir: str, name: str, version: str, 
               staging_dir: str, grid_credential: Optional[str] = None) -> None:
    """Manages datastores"""
    client = Grid()

    credential = get_credentials(client=client,
                                 grid_credential=grid_credential)

    client.upload_datastore(source_dir=source_dir,
                            staging_dir=staging_dir,
                            credential_id=credential['credentialId'],
                            name=name,
                            version=version)
