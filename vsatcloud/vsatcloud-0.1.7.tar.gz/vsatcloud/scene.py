import os
import time
from abc import ABC, abstractmethod

from .common import load_params, ensure_data_directories_exist, load_step_info, load_resources, get_file_name, \
    save_step_info, SHARE_PATH
from .logging import get_logger
logger = get_logger(__name__)


class ProcessingScene(ABC):
    """
    Base class for processing Scene.
    """
    @abstractmethod
    def process(self):
        raise NotImplementedError

    @classmethod
    def get_instance(cls, params):
        """
        获取实例
        """
        return cls(params)

    @classmethod
    def run(cls):
        """
        This method is the main entry point for the processing scene.
        """
        ensure_data_directories_exist()
        params: dict = load_params()
        step_info: dict = load_step_info()
        resources: dict = load_resources()
        algorithm_block = cls.get_instance(params)
        setattr(algorithm_block, "__resources", resources)
        setattr(algorithm_block, "__input_files", step_info)
        first_key = ""
        for key in step_info:
            first_key = key
            break
        output_file_path = algorithm_block.process(
            step_info[first_key])
        if output_file_path is None or not os.path.exists(output_file_path):
            file_name = "qwertyuiop.text"
        else:
            file_name = get_file_name(output_file_path)
            import shutil
            shutil.move(output_file_path, SHARE_PATH + "/" + file_name)  # 移动
        next_step_info = {"input_file_path": SHARE_PATH + "/" + file_name}
        save_step_info(next_step_info)


