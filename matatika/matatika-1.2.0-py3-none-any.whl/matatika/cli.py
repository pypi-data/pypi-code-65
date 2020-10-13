'''
Entry point for cli utility
'''

import click
import jwt
import pkg_resources
import requests
import yaml
from matatika.config import MatatikaConfig
from matatika.dataset_fields import DatasetItems
from matatika.exceptions import ContextNotSetError
from matatika.exceptions import MatatikaException
from matatika.exceptions import WorkspaceNotFoundError
from matatika.library import MatatikaClient

version = pkg_resources.require("matatika")[0].version


@click.group()
@click.version_option(version=version)
def start():  # pylint: disable=missing-function-docstring
    pass


@start.command('publish', short_help='Publish one or more dataset(s)')
@click.option('--workspace-id', '-w', type=click.UUID, help='Workspace ID')
# There is a type for file & path - we will loo into that option
@click.option('--dataset-file', '-f', type=click.Path(exists=True), required=True,
              help='Dataset file')
@click.option('--auth-token', '-a', help='Authentication token')
@click.option('--endpoint-url', '-u', help='Endpoint URL')
def publish(workspace_id, dataset_file, auth_token, endpoint_url):
    """Publish one or more dataset(s) from a YAML file into a workspace"""

    try:
        config = MatatikaConfig()
        if workspace_id is None:
            workspace_id = config.get_default_workspace()
        if auth_token is None:
            auth_token = config.get_auth_token()
        if endpoint_url is None:
            endpoint_url = config.get_endpoint_url()

        client = MatatikaClient(auth_token, endpoint_url, workspace_id)

        with open(dataset_file, 'r') as datasets_file:
            datasets = yaml.safe_load(datasets_file)[
                DatasetItems.DATASETS.value]

        publish_responses = client.publish(datasets)

        click.secho("Successfully published {} dataset(s)\n".format(len(publish_responses)),
                    fg='green')
        click.echo("{:<36}{:4}{:<36}{:4}{:<36}{:4}{:<36}".format(
            "DATASET ID", " ", "ALIAS", " ", "TITLE", " ", "STATUS"))

        for response in publish_responses:
            id_ = response.json()['id']
            alias = response.json()['alias']
            title = response.json()['title']

            if response.status_code == 200:
                status = click.style("UPDATED", fg='cyan')
            elif response.status_code == 201:
                status = click.style("NEW", fg='magenta')

            click.echo("{:<36}{:4}{:<36}{:4}{:<36}{:4}{:<36}".format(
                id_, " ", alias, " ", title, " ", status))

    except jwt.exceptions.DecodeError as err:
        click.secho(str(err), fg='red')
        click.secho(
            """Please check your authentication token is correct and valid""", fg='red')

    except requests.exceptions.HTTPError as err:
        click.secho(str(err), fg='red')
        click.secho("""Please check your authentication token has not expired and the correct
         endpoint is specified""", fg='red')

    except WorkspaceNotFoundError as err:
        click.secho(str(err), fg='red')

    except ContextNotSetError as err:
        click.secho(str(err), fg='red')


@start.command('list', short_help='List all available workspaces')
@click.option('--auth-token', '-a', help='Authentication token')
@click.option('--endpoint-url', '-e', help='Endpoint URL')
def list_(auth_token, endpoint_url):
    """Display a list of all available workspaces"""

    try:
        config = MatatikaConfig()
        if auth_token is None:
            auth_token = config.get_auth_token()
        if endpoint_url is None:
            endpoint_url = config.get_endpoint_url()

        client = MatatikaClient(auth_token, endpoint_url, None)

        workspaces = client.list_workspaces()

        click.echo("{:<36}{:4}{:<36}".format("WORKSPACE ID", " ", "NAME"))
        for workspace in workspaces:
            click.echo("{:<36}{:4}{:<36}".format(
                workspace['id'], " ", workspace['name']))

        click.echo("\nTotal workspaces: {}".format(len(workspaces)))

    except jwt.exceptions.DecodeError as err:
        click.secho(str(err), fg='red')
        click.secho(
            """Please check your authentication token is correct and valid""", fg='red')

    except requests.exceptions.HTTPError as err:
        click.secho(str(err), fg='red')
        click.secho("""Please check your authentication token has not expired and the correct
         endpoint is specified""", fg='red')

    except KeyError:
        click.secho("No workspaces found", fg='red')

    except ContextNotSetError as err:
        click.secho(str(err), fg='red')


@start.command('use', short_help='View or set the default workspace')
@click.option('--workspace-id', '-w', type=click.UUID, help='Workspace ID')
@click.option('--auth-token', '-a', help='Authentication token')
@click.option('--endpoint-url', '-e', help='Endpoint URL')
def use(workspace_id, auth_token, endpoint_url):
    """View or set the workspace context used by other commands"""

    try:
        config = MatatikaConfig()

        if workspace_id:
            if auth_token is None:
                auth_token = config.get_auth_token()
            if endpoint_url is None:
                endpoint_url = config.get_endpoint_url()

            client = MatatikaClient(auth_token, endpoint_url, None)
            workspaces = client.list_workspaces()

            workspace_id = str(workspace_id)
            workspace_ids = [workspaces[i]['id']
                             for i in range(len(workspaces))]

            if workspace_id not in workspace_ids:
                raise WorkspaceNotFoundError(workspace_id)

            config.set_default_workspace(workspace_id)

        workspace_context = config.get_default_workspace()
        click.secho("Workspace context set to {}".format(
            workspace_context), fg='green')

    except jwt.exceptions.DecodeError as err:
        click.secho(str(err), fg='red')
        click.secho(
            """Please check your authentication token is correct and valid""", fg='red')

    except requests.exceptions.HTTPError as err:
        click.secho(str(err), fg='red')
        click.secho("""Please check your authentication token has not expired and the correct
         endpoint is specified""", fg='red')

    except ContextNotSetError as err:
        click.secho(str(err), fg='red')

    except WorkspaceNotFoundError as err:
        click.secho(str(err), fg='red')

    except MatatikaException as err:
        click.secho(str(err), fg='red')


@start.command('login', short_help='Login to a Matatika account')
@click.option('--auth-token', '-a', required=True, help='Authentication token')
@click.option('--endpoint-url', '-e', default='https://catalog.matatika.com/api',
              help='Endpoint URL')
def login(auth_token, endpoint_url):
    """Login to a Matatika account and set the authentication context used by other commands"""

    try:
        client = MatatikaClient(auth_token, endpoint_url, None)
        profile = client.profile()

        config = MatatikaConfig()
        config.set_auth_token(auth_token)
        config.set_endpoint_url(endpoint_url)

        click.secho("Successfully logged in\n", fg='green')
        click.secho("{:<4}{:4}{}".format("ID", " ", profile['id']), fg='green')
        click.secho("{}{:4}{}".format(
            "NAME", " ", profile['name']), fg='green')

    except jwt.exceptions.DecodeError as err:
        click.secho(str(err), fg='red')
        click.secho(
            """Please check your authentication token is correct and valid""", fg='red')

    except requests.exceptions.HTTPError as err:
        click.secho(str(err), fg='red')
        click.secho("""Please check your authentication token has not expired and the correct
         endpoint is specified""", fg='red')


if __name__ == '__main__':
    start()
