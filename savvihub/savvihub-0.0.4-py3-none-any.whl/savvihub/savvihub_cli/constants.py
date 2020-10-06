import os
from pathlib import Path


# HOST_URL = 'http://13.125.213.13:10000'
# HOST_URL = 'http://localhost:10000'
HOST_URL = 'http://def13d9cd74e.ngrok.io'
CLIENT_URL = 'http://localhost:3000'
CUR_DIR = os.getcwd()
DEFAULT_SAVVI_DIR = os.path.join(str(Path.home()), '.savvihub')
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_SAVVI_DIR, 'config.yml')

DEFAULT_SAVVIHUBFILE_YAML = 'savvihubfile.yml'
INQUIRER_NAME_IMAGE = 'image'
INQUIRER_NAME_RESOURCE = 'resource'
INQUIRER_NAME_DATASET = 'dataset'
INQUIRER_NAME_DATASET_REF = 'dataset_ref'
INQUIRER_NAME_DATASET_MOUNT_PATH = 'dataset_mount_path'
INQUIRER_NAME_COMMAND = 'command'
