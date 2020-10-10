import json
import os
import pathlib
import re

from .logging import get_logger

logger = get_logger(__name__)
SHARE_PATH = "/mnt/disks/argo"
workflow_name = os.environ.get("WORKFLOW_NAME", "")
SHARE_PATH = SHARE_PATH + "/" + workflow_name
STEP_INFO_PATH = SHARE_PATH + "/step-info.json"


def ensure_data_directories_exist():
    """
    创建必须文件夹
    """
    pathlib.Path(SHARE_PATH).mkdir(parents=True, exist_ok=True)


def load_params():
    """
    获取参数
    """
    data: str = os.environ.get("VSAT_STEP_PARAMETERS", "{}").replace("'", '"')
    logger.info("Fetching parameters for this block: %s", data)
    if data == "":
        data = "{}"
    return json.loads(data)


def save_step_info(result):
    """
    持久化步骤信息
    """
    with open(STEP_INFO_PATH, "w") as fp:
        fp.write(json.dumps(result))


def load_step_info():
    """
    获取步骤信息
    """
    ensure_data_directories_exist()
    if os.path.exists(STEP_INFO_PATH):
        with open(STEP_INFO_PATH) as fp:
            data = json.loads(fp.read())

        return data
    else:
        return None


def get_file_name(path_string):
    """获取文件名称"""
    return os.path.basename(path_string)


def load_resources():
    """
    获取resources
    """
    data: str = os.environ.get("VSAT_RESOURCES_INFO", "{}").replace("'", '"')
    logger.info("Fetching resources for this block: %s", data)
    if data == "":
        data = "{}"
    return json.loads(data)
