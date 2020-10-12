import typer
from terminaltables import AsciiTable
import inquirer

from savvihub.savvihub_cli.inquirer import get_choices, parse_id
from savvihub.savvihub_cli.savvihub import SavviHubClient
from savvihub.savvihub_cli.constants import DEFAULT_CONFIG_PATH, CUR_DIR, INQUIRER_NAME_IMAGE, INQUIRER_NAME_RESOURCE, \
    INQUIRER_NAME_COMMAND, CLIENT_URL, INQUIRER_NAME_DATASET, INQUIRER_NAME_DATASET_REF, \
    INQUIRER_NAME_DATASET_MOUNT_PATH, DEFAULT_SAVVIHUBFILE_YAML
from savvihub.savvihub_cli.errors import get_error_message
from savvihub.savvihub_cli.utils import *
from savvihub.savvihub_cli.yml_loader import ExperimentYmlLoader

experiment_app = typer.Typer()


@experiment_app.callback()
def main():
    """
    Perform your experiment with Savvihub
    """
    return


@experiment_app.command()
def init(
        slug: str = typer.Argument(..., help="Type workspace/project as an argument"),
        file: str = typer.Option(DEFAULT_SAVVIHUBFILE_YAML, "--file", "-f"),
):
    """
    Initialize a new experiment configuration file with workspace/project
    """
    # Remove old config file if exists
    config_file_path = os.path.join(CUR_DIR, file)
    remove_file(config_file_path)

    workspace, project = slug.split("/")
    data = {
        'workspace': workspace,
        'project': project,
    }

    make_file(config_file_path)
    yml_loader = ExperimentYmlLoader(config_file_path)
    yml_loader.write(data)

    typer.echo(f"Experiment config successfully made in {config_file_path}")


@experiment_app.command()
def data_mount(
        file: str = typer.Option(DEFAULT_SAVVIHUBFILE_YAML, "--file", "-f"),
):
    """
    Mount data to experiment
    """
    config_file_path = os.path.join(CUR_DIR, file)
    if not os.path.exists(config_file_path):
        raise Exception('Initialize experiment with this command: $ savvi experiment init SLUG')

    token = get_token_from_config(DEFAULT_CONFIG_PATH)
    client = SavviHubClient(token=token)

    yml_loader = ExperimentYmlLoader(file)

    questions = [
        inquirer.List(
            INQUIRER_NAME_DATASET,
            message="Please choose a dataset",
            choices=get_choices(client, 'dataset', yml_loader),
        ),
        inquirer.Text(
            INQUIRER_NAME_DATASET_REF,
            message="Dataset ref",
            default=yml_loader.data.get('dataset_mount_ref', 'latest'),
        ),
        inquirer.Text(
            INQUIRER_NAME_DATASET_MOUNT_PATH,
            message="Dataset mount path",
            default=yml_loader.data.get('dataset_mount_path', 'input'),
        ),
    ]

    answers = inquirer.prompt(questions)
    dataset_mount_id = parse_id(answers.get(INQUIRER_NAME_DATASET))

    yml_loader.update_and_write({
        'data_mount_infos': {
            'id': dataset_mount_id,
            'ref': answers.get(INQUIRER_NAME_DATASET_REF),
            'mount_path': answers.get(INQUIRER_NAME_DATASET_MOUNT_PATH),
        }
    })


@experiment_app.command()
def list(
        file: str = typer.Option(DEFAULT_SAVVIHUBFILE_YAML, "--file", "-f"),
):
    """
    List of experiments
    """
    token = get_token_from_config(DEFAULT_CONFIG_PATH)
    client = SavviHubClient(token=token)
    yml_loader = ExperimentYmlLoader(file)

    workspace = yml_loader.data.get('workspace')
    project = yml_loader.data.get('project')

    resp = client.experiment_list(workspace, project, raise_error=True)
    experiments = resp.json().get('results')
    table = AsciiTable([
        ['Number', 'Status', 'Message'],
        *[[e.get('number'), e.get('status'), e.get('message')] for e in experiments],
    ])
    typer.echo(table.table)


@experiment_app.command()
def log(
        file: str = typer.Option(DEFAULT_SAVVIHUBFILE_YAML, "--file", "-f"),
        experiment_number: int = typer.Argument(...),
):
    """
    View experiment logs
    """
    token = get_token_from_config(DEFAULT_CONFIG_PATH)
    client = SavviHubClient(token=token)
    yml_loader = ExperimentYmlLoader(file)

    workspace = yml_loader.data.get('workspace')
    project = yml_loader.data.get('project')

    resp = client.experiment_log(workspace, project, experiment_number, raise_error=True)
    print(resp.text)


@experiment_app.command()
def run(
        file: str = typer.Option(DEFAULT_SAVVIHUBFILE_YAML, "--file", "-f"),
):
    """
    Run an experiment in Savvihub
    """
    if not is_committed():
        raise Exception('You should commit diffs before run an experiment!')

    config_file_path = os.path.join(CUR_DIR, file)
    if not os.path.exists(config_file_path):
        raise Exception('Initialize experiment with this command: $ savvi experiment init SLUG')

    token = get_token_from_config(DEFAULT_CONFIG_PATH)
    client = SavviHubClient(token=token)

    yml_loader = ExperimentYmlLoader(file)

    if not yml_loader.is_ready_to_run():
        raise Exception('You should mount data first with this command: $ savvi experiment data-mount')

    questions = [
        inquirer.List(
            INQUIRER_NAME_IMAGE,
            message="Please choose a kernel image",
            choices=get_choices(client, 'image', yml_loader),
        ),
        inquirer.List(
            INQUIRER_NAME_RESOURCE,
            message="Please choose a kernel resource",
            choices=get_choices(client, 'resource', yml_loader),
        ),
        inquirer.Text(
            INQUIRER_NAME_COMMAND,
            message="Start command",
            default="python main.py",
        )
    ]

    answers = inquirer.prompt(questions)
    image_id = parse_id(answers.get(INQUIRER_NAME_IMAGE))
    resource_spec_id = parse_id(answers.get(INQUIRER_NAME_RESOURCE))

    yml_loader.update_and_write({
        'image_id': image_id,
        'resource_spec_id': resource_spec_id,
        'start_command': answers.get(INQUIRER_NAME_COMMAND),
    })

    res = client.experiment_create(
        workspace=yml_loader.data.get('workspace'),
        project=yml_loader.data.get('project'),
        image_id=int(yml_loader.data.get('image_id')),
        resource_spec_id=int(yml_loader.data.get('resource_spec_id')),
        branch=get_git_revision_hash(),
        dataset_mount_infos=[{
            'id': int(dataset_mount_info.get('id')),
            'ref': dataset_mount_info.get('ref'),
            'mount_path': dataset_mount_info.get('mount_path'),
        } for dataset_mount_info in yml_loader.data.get('data_mount_infos')],
        start_command=yml_loader.data.get('start_command'),
    )

    res_data = res.json()
    if res.status_code == 400:
        typer.echo(get_error_message(res_data))
        return
    res.raise_for_status()

    experiment_number = res_data.get('number')
    typer.echo(f"Experiment {experiment_number} is running. Check the experiment status at below link")
    typer.echo(f"{CLIENT_URL}/{yml_loader.data.get('workspace')}/{yml_loader.data.get('project')}/"
               f"experiments/{experiment_number}")
    return


if __name__ == "__main__":
    experiment_app()
