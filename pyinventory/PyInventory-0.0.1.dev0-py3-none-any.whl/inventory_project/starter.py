import sys
from pathlib import Path

import click

# https://github.com/jedie/PyInventory
import inventory
from inventory_project.utils.venv import VirtualEnvPath


SVG_LOGO = "static/PyInventory.svg"  # .../inventory/static/PyInventory.svg

XDG_OPEN_FILENAME_NORMAL = "PyInventory"
XDG_OPEN_FILENAME_DEVELOP = "PyInventory develop"
XDG_OPEN_TEMPLATE = """#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Icon={svg_logo_path}
Exec=x-terminal-emulator -e "{inventory_exe} {command}"
Name={name}
"""

# gnome-terminal -x bash -c '/usr/bin/cal && bash'


def get_inventory_app_path():
    inventory_app_path = Path(inventory.__file__).parent
    return inventory_app_path


def get_svg_logo_path():
    inventory_app_path = get_inventory_app_path()
    svg_logo_path = Path(inventory_app_path, SVG_LOGO)
    assert svg_logo_path.is_file(), f"Logo not found here: {svg_logo_path}"
    return svg_logo_path


def create_linux_xdg_open_file(file_name, inventory_exe, command, env_path):
    desktop_file_path = Path(env_path, f"{file_name}.desktop")
    print(f"Create linux xdg-open starter here: {desktop_file_path}")

    svg_logo_path = get_svg_logo_path()
    content = XDG_OPEN_TEMPLATE.format(
        name=file_name, svg_logo_path=svg_logo_path, inventory_exe=inventory_exe, command=command
    )
    with desktop_file_path.open("w") as f:
        f.write(content)
    desktop_file_path.chmod(0o777)


def create_starter():
    click.echo("Create stater")

    venv_path = VirtualEnvPath()
    env_path = venv_path.env_path
    print(f"Create starter in: {env_path}")

    inventory_exe = venv_path.get_inventory_exe()

    if sys.platform in ("win32", "cygwin"):
        raise NotImplementedError("TODO: Create starter under Windows!")
    else:
        create_linux_xdg_open_file(XDG_OPEN_FILENAME_NORMAL, inventory_exe, "run_gunicorn", env_path)
        create_linux_xdg_open_file(XDG_OPEN_FILENAME_DEVELOP, inventory_exe, "run_dev_server", env_path)
