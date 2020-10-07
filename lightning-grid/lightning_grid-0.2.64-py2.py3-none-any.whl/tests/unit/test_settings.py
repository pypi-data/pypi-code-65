import os
import grid.globals as env
from grid.client import Grid

from pathlib import Path
from tests.utilities import create_local_schema_client

SETTINGS_PATH = 'tests/data/settings.json'
CREDENTIALS_PATH = 'tests/data/credentials.json'


def monkey_patch_client(self):
    self.client = create_local_schema_client()


#  skipcq: PYL-W0212
Grid._init_client = monkey_patch_client


def test_load_global_settings():
    """Grid() loads global settings alters globals."""

    Grid.grid_settings_path = SETTINGS_PATH
    Grid(credential_path=CREDENTIALS_PATH, load_local_credentials=False)

    assert env.DEBUG == False


def test_global_settings_create_file_if_not_exists():
    """Grid() creates file if not exists."""

    new_path = 'tests/data/home/settings.json'
    Grid.grid_settings_path = new_path
    Grid(credential_path=CREDENTIALS_PATH, load_local_credentials=False)

    P = Path.home().joinpath(new_path)
    assert P.exists()

    # cleanup
    P.unlink()
