import os
import tarfile
from distutils.dir_util import copy_tree

import click
import requests

from smls.api_key import get_api_key, set_api_key, is_api_key_valid
from smls.constants import ARCHIVE_FOR_SENDING_NAME, SEAMLESS_SERVICE_URL, ARCHIVE_SIZE_LIMIT, \
    EXCLUDE_FOLDERS_AND_FILES, SEAMLESS_SERVICE_PUBLISH_ROUTE, SEAMLESS_HOST, \
    SEAMLESS_SERVICE_JOBS_ROUTE, DEFAULT_ENTRYPOINT_FILENAME, DEFAULT_REQUIREMENTS_FILE


def _package_project(folder_to_archive):
    def filtr(file):
        for name in EXCLUDE_FOLDERS_AND_FILES:
            if file.name.startswith(f"./{name}"):
                return None
        return file

    tar = tarfile.open(ARCHIVE_FOR_SENDING_NAME, "w:gz")
    tar.add(folder_to_archive, filter=filtr)
    tar.close()
    # TODO we should have this limit only on server side and return meaningful error
    # TODO it should be doable with the production WSGI server and catching 413 error
    if os.stat(ARCHIVE_FOR_SENDING_NAME).st_size > ARCHIVE_SIZE_LIMIT:
        print(f"Your project is too big."
              f" After we compressed the folder {folder_to_archive} the resulting file is more than 10 MB."
              f"In order to have a really seamless experience we recommend to remove non-essential files."
              f"If you need to increase the limit - please shoot us an email at hello@seamlesscloud.io")
        exit(1)
    return ARCHIVE_FOR_SENDING_NAME


@click.group()
# This is just an entry point for the CLI, all other commands are registered in this group
def cli():
    pass


@cli.command()
@click.option(
    "-n",
    "--name",
    help="name of the job you want to publish",
    required=True
)
@click.option(
    "-s",
    "--schedule",
    help="cron expression that identifies the schedule your code runs on",
)
@click.option('-e', '--entrypoint', default=DEFAULT_ENTRYPOINT_FILENAME, help='Name of the entrypoint file')
@click.option('-r', '--requirements', default=DEFAULT_REQUIREMENTS_FILE, help='Path to the file with requirements')
def publish(name, schedule, entrypoint, requirements):
    api_key = get_api_key()
    package_name = None
    try:
        package_name = _package_project(folder_to_archive='.')
        params = {'name': name, 'entrypoint': entrypoint, 'requirements': requirements}
        if schedule:
            params.update({'schedule': schedule})
        resp = requests.put(SEAMLESS_SERVICE_URL + SEAMLESS_SERVICE_PUBLISH_ROUTE,
                            params=params,
                            headers={'Authorization': api_key},
                            files={'seamless_project': open(package_name, 'rb')})
        handle_server_response(resp)
        data = resp.json()
        link_to_job = f"{SEAMLESS_HOST}/jobs/{data['job_id']}"
        if not data['existing_job']:
            click.echo(f"Congratulations, you have created a new job. "
                       f"You can find it at {link_to_job}")
        else:
            click.echo(f"Congratulations, you have updated your '{name}' job. "
                       f"You can find it at {link_to_job}")
    finally:
        try:
            if package_name:
                os.remove(package_name)
        except OSError:
            pass


@cli.command()
@click.option(
    "--name",
    help="name of the job you want to remove",
    required=True
)
def remove(name):
    api_key = get_api_key()
    resp = requests.delete(SEAMLESS_SERVICE_URL + SEAMLESS_SERVICE_JOBS_ROUTE + f'/{name}',
                           headers={'Authorization': api_key})
    handle_server_response(resp)
    click.echo(f"Job '{name}' was removed.")


@cli.command()
@click.argument('api_key')
def auth(api_key):
    if not is_api_key_valid(api_key):
        click.echo("The API KEY provided is not valid. "
                   "API key should be a sting exactly 20 characters long.")
        exit(0)
    set_api_key(api_key)

    click.echo("Welcome to the Seamless Cloud community!")


@cli.command()
def example():
    example_job_folder_name = 'stock_monitoring_job'
    source = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          'example_job')
    destination = os.path.join(os.getcwd(), example_job_folder_name)
    copy_tree(source, destination)

    click.echo(f"Example job was created! Now let's publish it. In the terminal do the following:")
    click.echo(f"1. 'cd {example_job_folder_name}' - to go into the folder with the example job")
    click.echo(f"2. 'smls publish --name \"Stock Price Monitoring\" --schedule \"0 0 * * *\"' - "
               f"to run the job every day at 00:00 UTC."
               f" You need to be inside the folder with the job definition for this command to work.")


def handle_server_response(resp):
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        if resp.status_code == 500:
            click.echo("Oops, there was an error on the server side. We are already investigating."
                       "If you want to be up to date on the fix status, please email us at hello@seamlesscloud.io.")
        else:
            click.echo(resp.text)
        exit(1)
