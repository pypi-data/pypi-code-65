import os
import shutil
import tempfile
from pathlib import Path

import click

from ..decorators import loses_interactivity, require_login
from ..helpers.config import Config
from ..helpers.contexts import push_envs
from ..helpers.doctor import (
    AnsibleDoctorRunner,
    check_saml_client,
    deliver_logs,
    logs_dir,
    self_update,
    write_host_info,
    write_versions,
    write_versions_pip,
    zip_logs,
)
from ..helpers.global_options import GlobalOptions
from ..helpers.options import resource_argument
from .sym import sym


@sym.command(hidden=True, short_help="run diagnostics")
@resource_argument
@click.option(
    "--mode", required=True, type=click.Choice(["basic", "ansible"]), default="basic"
)
@click.option("--inventory", type=click.Path(file_okay=True, dir_okay=False, exists=True))
@click.option("--playbook", type=click.Path(file_okay=True, dir_okay=False, exists=True))
@click.option(
    "--output-dir",
    required=True,
    default=str(Path.home() / "Desktop"),
    type=click.Path(file_okay=False, dir_okay=True, exists=True),
)
@click.option("--timeout", type=int, default=60)
@click.option("--did-update", is_flag=True, default=False, hidden=True)
@click.make_pass_decorator(GlobalOptions)
@loses_interactivity
@require_login
def doctor(
    options: GlobalOptions,
    resource: str,
    mode: str,
    playbook: str,
    inventory: str,
    output_dir: str,
    timeout: int,
    did_update: bool,
):
    click.secho(
        f"Hey {Config.get_handle()}! Hope you're having a fantastic day :-)",
        fg="cyan",
        bold=True,
    )

    if not did_update:
        self_update()

    click.echo("Setting up test environment...")
    client = options.create_saml_client(resource)
    temp_dir = Path(tempfile.mkdtemp())
    doctor_dir = logs_dir(temp_dir)

    click.echo("Checking binary versions...")
    write_versions(doctor_dir / "versions.txt")

    click.echo("Checking Pip versions...")
    write_versions_pip(doctor_dir / "pip_versions.txt")

    click.echo("Checking SAML client...")
    check_saml_client(client, doctor_dir / "saml_client.txt")

    ssh_config_path = os.path.join(str(Path.home()), ".ssh", "config")
    if os.path.exists(ssh_config_path):
        click.echo("Copying SSH configuration...")
        shutil.copy(ssh_config_path, doctor_dir / "ssh_config")

    click.echo(f"Running {mode} checks...")
    with push_envs({"SYM_LOG_DIR": str(doctor_dir / "logs"), "SYM_DEBUG": "true"}):
        if mode == "ansible":
            AnsibleDoctorRunner(client, doctor_dir, timeout).run(inventory, playbook)

    click.echo("Checking host info...")
    write_host_info(doctor_dir / "host_info.txt")

    click.echo("Zipping it all up...")
    zip = zip_logs(doctor_dir)
    output = deliver_logs(client, Path(output_dir), zip)

    click.secho(f"Done! Your archive is at {str(output)}.", fg="green", bold=True)
