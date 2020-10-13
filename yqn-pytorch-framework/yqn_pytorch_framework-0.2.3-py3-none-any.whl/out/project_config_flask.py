import os

from yqn_pytorch_framework.device import get_device

TENSOR_RT = False
VERBOSE = True
os.environ["IN_DOCKER"] = "Y"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# 工程路径
PROJECT_BASE_DIR = './'

# resource_path
RESOURCE_BASE_DIR = os.path.join(PROJECT_BASE_DIR, 'resources')

# output_path
OUTPUT_BASE_DIR = os.path.join(PROJECT_BASE_DIR, 'outputs')

SWITCH = {

}


class LocalConfig:

    def __init__(self):
        self.project_path = PROJECT_BASE_DIR
        self.resource_path = RESOURCE_BASE_DIR
        self.output_path = OUTPUT_BASE_DIR
        self.switch = SWITCH
        self.tensorrt = TENSOR_RT

        get_device(VERBOSE)

