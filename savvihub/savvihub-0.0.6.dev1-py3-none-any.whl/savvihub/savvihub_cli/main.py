import requests
import typer

from savvihub.savvihub_cli.artifact import artifact_app
from savvihub.savvihub_cli.config import config
from savvihub.savvihub_cli.constants import HOST_URL, DEFAULT_SAVVI_DIR, DEFAULT_CONFIG_PATH
from savvihub.savvihub_cli.dataset import dataset_app
from savvihub.savvihub_cli.errors import get_error_message
from savvihub.savvihub_cli.experiment import experiment_app
from savvihub.savvihub_cli.utils import *

app = typer.Typer()
app.add_typer(experiment_app, name="experiment")
app.add_typer(dataset_app, name="dataset")
app.add_typer(artifact_app, name="artifact")
__version__ = '0.0.4'


def version_callback(value: bool):
    if value:
        typer.echo(f"Savvihub CLI Version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True),
):
    """
    Savvihub command line interface
    """

    return


@app.command()
def ping():
    """
    Ping to server
    """
    res = requests.get(HOST_URL + '/v1/api/ping/')
    typer.echo(f"Response code: {res.status_code}, Response text: {res.text}")


@app.command()
def init(
    token: str = typer.Option(config.token, "-t", "--token")
):
    """
    Initialize with an access token issued from SavviHub
    """
    if token is None:
        token = typer.prompt('token')

    data = {
        'token': token
    }

    make_dir(DEFAULT_SAVVI_DIR)
    with open(DEFAULT_CONFIG_PATH, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

    typer.echo(f"Token successfully saved in {DEFAULT_CONFIG_PATH}")
