# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyklopp', 'pyklopp.console', 'pyklopp.console.commands']

package_data = \
{'': ['*'], 'pyklopp': ['schema/*']}

install_requires = \
['cleo>=0.7,<0.8',
 'importlib-metadata>=1.5.0,<2.0.0',
 'importlib-resources>=1.4.0,<2.0.0',
 'jsonschema>=3.2.0,<4.0.0',
 'pytorch-ignite>=0.2,<0.3',
 'semantic_version>=2.8.4,<3.0.0',
 'torch>=1.3',
 'torchvision>=0.4',
 'tqdm>=4.40,<5.0']

entry_points = \
{'console_scripts': ['pyklopp = pyklopp.console:main']}

setup_kwargs = {
    'name': 'pyklopp',
    'version': '0.3.2',
    'description': '',
    'long_description': '# pyklopp [![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity) [![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/) [![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/) [![Python 3.6](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/) ![Tests](https://github.com/innvariant/pyklopp/workflows/Tests/badge.svg)\nTired of logging all hyperparameter configurations of your model prototyping to disk?\n\nPyklopp is a tool to initialize, train and evaluate pytorch models (currently for supervised problems).\nIt persists all relevant hyperparameters, timings and model configurations.\nYour prototyping is reduced to defining your model, the dataset and your desired parameters.\n\n**Important note:** we are undergoing an architectural change from writing config json files to writing meta data files given a jsonschema.\nSo to keep your experiments reproducible and program against a current design of pyklopp, reference the exact pyklopp version in your experiment.\nE.g. for your *environment.yml*:\n```yaml\ndependencies:\n- pip:\n  - pyklopp==0.3.0\n```\n\n![Workflow sketch for developing a model and running it with pyklopp.](res/approach.png)\n\n\n## Installation\nYou can install a version from PyPi with: ``pip install pyklopp``.\n\nTo install the latest development build, you can clone the repository and invoke ``poetry build`` (having poetry installed).\nThen you can use the built package and install it with pip in your current environment by ``pip install dist/xxx.whl``.\n\n\n# Defining model & dataset\nUsed imports:\n```python\nimport pypaddle.sparse\nimport pypaddle.util\nimport torch.nn as nn\nimport torch.nn.functional as F\n\n```\nSpecify your model in a plain python file, e.g.:\n```python\n# my_model.py\n\n# Your model can be any pytorch module\n# Make sure to not define it locally (e.g. within the get_model()-function)\nclass LeNet(nn.Module):\n    def __init__(self, output_size):\n        super(LeNet, self).__init__()\n        self.conv1 = nn.Conv2d(3, 6, 5)\n        self.conv2 = nn.Conv2d(6, 16, 5)\n        self.fc1 = nn.Linear(16 * 5 * 5, 120)\n        self.fc2 = nn.Linear(120, 84)\n        self.fc3 = nn.Linear(84, output_size)\n\n    def forward(self, x):\n        out = F.relu(self.conv1(x))\n        out = F.max_pool2d(out, 2)\n        out = F.relu(self.conv2(out))\n        out = F.max_pool2d(out, 2)\n        out = out.view(out.size(0), -1)\n        out = F.relu(self.fc1(out))\n        out = F.relu(self.fc2(out))\n        out = self.fc3(out)\n        return out\n\n\n# This is your model-instantiation function\n# It receives an assembled configuration keyword argument list and should return an instance of your model\ndef get_model(**kwargs):\n    output_size = int(kwargs[\'output_size\'])\n\n    return LeNet(output_size)\n```\n\nInvoke pyklopp to initialize it: ``pyklopp init my_model.get_model --save=\'test/model.pth\' --config=\'{"output_size": 10}\'``\nTrain it on *cifar10*:\n- ``pyklopp train test/model.pth cifar10.py --save=\'test/trained.pth\' --config=\'{"batch_size": 100}\'``\n- ``pyklopp train test/model.pth torchvision.datasets.cifar.CIFAR10 --save \'test/trained.pth\' --config=\'{"dataset_root": "/media/data/set/cifar10"}\'``\n\n\n# Examples\n\n```bash\n# Initializing & Saving: mymodel.py\npyklopp init foo --save=\'mymodel1/model.pth\'\npyklopp init foo --config=\'{"python_seed_initial": 100}\' --save=\'mymodel2/model.pth\'\n\n# Training\npyklopp train path/to/mymodel.pth mnist\npyklopp train path/to/mymodel.pth mnist --config=\'{"batch_size": 100, "learning_rate": 0.01}\'\n```\n\n```python\n# foo.py - Your model initialization function\n\ndef init(**kwargs):\n    input_size = kwargs[\'input_size\']\n    output_size = kwargs[\'output_size\']\n\n    return pypaddle.sparse.MaskedDeepFFN(input_size, output_size, [100, 100])\n```\n\n```python\n# mnist.py - Your dataset loading functions\n\ndef train_loader(**kwargs):\n    batch_size = kwargs[\'batch_size\']\n\n    mnist_train_loader, mnist_test_loader, _, selected_root = pypaddle.util.get_mnist_loaders(batch_size, \'/media/data/set/mnist\')\n    return mnist_train_loader\n\n\ndef test_loader(**kwargs):\n    batch_size = kwargs[\'batch_size\']\n\n    mnist_train_loader, mnist_test_loader, _, selected_root = pypaddle.util.get_mnist_loaders(batch_size, \'/media/data/set/mnist\')\n    return mnist_test_loader\n```\n\n\n# Development\n- Create wheel files in *dist/*: ``poetry build``\n- Install wheel in current environment with pip: ``pip install path/to/pyklopp/dist/pyklopp-0.1.0-py3-none-any.whl``\n\n## Running CI image locally\nInstall latest *gitlab-runner* (version 12.3 or up):\n```bash\n# For Debian/Ubuntu/Mint\ncurl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash\n\n# For RHEL/CentOS/Fedora\ncurl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.rpm.sh | sudo bash\n\napt-get update\napt-get install gitlab-runner\n\n$ gitlab-runner -v\nVersion:      12.3.0\n```\nExecute job *tests*: ``gitlab-runner exec docker test-python3.6``\n\n## Running github action locally\nInstall *https://github.com/nektos/act*.\nRun ``act``\n\n## Running pre-commit checks locally\n``poetry run pre-commit run --all-files``\n',
    'author': 'Julian Stier',
    'author_email': 'julian.stier@uni-passau.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/innvariant/pyklopp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
