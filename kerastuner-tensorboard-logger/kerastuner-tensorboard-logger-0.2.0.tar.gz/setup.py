# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kerastuner_tensorboard_logger']

package_data = \
{'': ['*']}

install_requires = \
['keras-tuner>=1.0,<2.0', 'tensorflow>=2.0,<3.0']

setup_kwargs = {
    'name': 'kerastuner-tensorboard-logger',
    'version': '0.2.0',
    'description': 'Simple integration of keras-tuner (hyperparameter tuning) and tensorboard dashboard (interactive visualization).',
    'long_description': '# Keras-tuner Tensorboard logger\n\n![](https://github.com/tokusumi/kerastuner-tensorboard-logger/workflows/Tests/badge.svg)\n[![PyPI version](https://badge.fury.io/py/kerastuner-tensorboard-logger.svg)](https://badge.fury.io/py/kerastuner-tensorboard-logger)\n\n[keras-tuner](https://www.tensorflow.org/tutorials/keras/keras_tuner) logger for streaming search report to [Tensorboard plugins Hparams](https://www.tensorflow.org/tensorboard/hyperparameter_tuning_with_hparams), beautiful interactive visualization tool.\n\n## Requirements\n\n* Python 3.6+\n* keras-tuner 1.0.0+\n* Tensorboard 2.1+\n\n## Installation\n\n```\n$ pip install kerastuner-tensorboard-logger\n```\n\n## Example\n\nhere is simple (and incomplete) code.\n\nSee details about how to use keras-tuner [here](https://github.com/keras-team/keras-tuner).\n\nAdd only one argument in tuner class and search it, then you can go to see search report in Tensorboard.\n\nOptionally, you can call `setup_tb` to be more accurate TensorBoard visualization. It convert keras-tuner hyperparameter information and do [Tensorboard experimental setup](https://www.tensorflow.org/tensorboard/hyperparameter_tuning_with_hparams#1_experiment_setup_and_the_hparams_experiment_summary).\n\n```python\n# import this\nfrom kerastuner_tensorboard_logger import (\n    TensorBoardLogger,\n    setup_tb  # Optional\n)\n\ntuner = Hyperband(\n    build_model,\n    objective="val_acc",\n    max_epochs=5,\n    directory="logs/tuner",\n    project_name="tf_test",\n    logger=TensorBoardLogger(\n        metrics=["val_acc"], logdir="logs/hparams"\n    ),  # add only this argument\n)\n\nsetup_tb(tuner)  # (Optional) For more accurate visualization.\ntuner.search(x, y, epochs=5, validation_data=(val_x, val_y))\n```\n\n### Tensorboard\n\n```bash\n$ tensorboard --logdir ./logs/hparams\n```\n\nGo to http://127.0.0.1:6006.\n\nYou will see the interactive visualization (provided by Tensorboard).\n\n![Table View](https://raw.githubusercontent.com/tokusumi/kerastuner-tensorboard-logger/main/docs/src/table_view.jpg)\n\n![Parallel Coordinates View](https://raw.githubusercontent.com/tokusumi/kerastuner-tensorboard-logger/main/docs/src/parallel_coordinates_view.jpg)\n',
    'author': 'tokusumi',
    'author_email': 'tksmtoms@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tokusumi/kerastuner-tensorboard-logger',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
