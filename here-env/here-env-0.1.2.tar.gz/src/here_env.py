import os
import pathlib
import subprocess
import venv

import click


@click.command()
@click.option("--prompt")
def cli(prompt):
    active_venv = os.environ.get("VIRTUAL_ENV")
    if active_venv:
        click.echo(f"Virtualenv '{active_venv}' already active", err=True)
        return

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True
        )
        work_root = pathlib.Path(result.stdout.decode("utf-8").strip())
    except subprocess.CalledProcessError:
        work_root = pathlib.Path(".")

    work_root = work_root.resolve()
    venv_dir = work_root / ".venv"

    if not venv_dir.exists():
        click.echo(f"Creating new venv in '{venv_dir}'", err=True)
        prompt = prompt or work_root.name
        venv.create(venv_dir, prompt=prompt)

    activate_script = venv_dir / "bin/activate"
    click.echo(f"Activating '{venv_dir}'", err=True)
    click.echo(f". '{activate_script}'")
