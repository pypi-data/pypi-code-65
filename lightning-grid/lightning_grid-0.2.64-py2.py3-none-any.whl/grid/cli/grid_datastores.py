import click

from grid import Grid


@click.command()
@click.option('--source_dir',
              type=click.Path(exists=True, file_okay=True, dir_okay=True),
              required=True,
              help='Source directory to upload datastore files')
@click.option('--name', type=str, required=True, help='Name of the datastore')
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
               staging_dir: str) -> None:
    """Manages datastores"""
    client = Grid()
    client.upload_datastore(source_dir=source_dir,
                            staging_dir=staging_dir,
                            name=name,
                            version=version)
