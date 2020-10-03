# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['icevision',
 'icevision.backbones',
 'icevision.core',
 'icevision.data',
 'icevision.engines',
 'icevision.engines.fastai',
 'icevision.engines.fastai.adapters',
 'icevision.engines.fastai.learner',
 'icevision.engines.lightning',
 'icevision.metrics',
 'icevision.metrics.coco_metric',
 'icevision.models',
 'icevision.models.efficientdet',
 'icevision.models.efficientdet.fastai',
 'icevision.models.efficientdet.lightning',
 'icevision.models.rcnn',
 'icevision.models.rcnn.fastai',
 'icevision.models.rcnn.faster_rcnn',
 'icevision.models.rcnn.faster_rcnn.fastai',
 'icevision.models.rcnn.faster_rcnn.lightning',
 'icevision.models.rcnn.lightning',
 'icevision.models.rcnn.mask_rcnn',
 'icevision.models.rcnn.mask_rcnn.fastai',
 'icevision.models.rcnn.mask_rcnn.lightning',
 'icevision.parsers',
 'icevision.parsers.mixins',
 'icevision.test_utils',
 'icevision.tfms',
 'icevision.tfms.albumentations',
 'icevision.tfms.batch',
 'icevision.utils',
 'icevision.visualize']

package_data = \
{'': ['*']}

install_requires = \
['albumentations>=0.4.6,<0.5.0',
 'fastcore>=1.0.14,<2.0.0',
 'matplotlib>=3.3.2,<4.0.0',
 'opencv-python>=4.4.0,<5.0.0',
 'pycocotools>=2.0.2,<3.0.0',
 'requests>=2.24.0,<3.0.0',
 'torch>=1.6.0,<1.7.0',
 'torchvision>=0.7.0,<0.8.0',
 'tqdm>=4.49.0,<5.0.0']

extras_require = \
{'all': ['fastai>=2.0.13',
         'ipykernel>=5.3.4,<6.0.0',
         'pytorch-lightning>=0.9,<0.10',
         'effdet>=0.1.6,<0.2.0',
         'omegaconf>=2.0.0,<3.0.0',
         'dataclasses==0.6'],
 'fastai': ['fastai>=2.0.13', 'ipykernel>=5.3.4,<6.0.0'],
 'inference': ['effdet>=0.1.6,<0.2.0',
               'omegaconf>=2.0.0,<3.0.0',
               'dataclasses==0.6'],
 'lightning': ['pytorch-lightning>=0.9,<0.10'],
 'models': ['effdet>=0.1.6,<0.2.0',
            'omegaconf>=2.0.0,<3.0.0',
            'dataclasses==0.6'],
 'training': ['fastai>=2.0.13',
              'ipykernel>=5.3.4,<6.0.0',
              'pytorch-lightning>=0.9,<0.10',
              'effdet>=0.1.6,<0.2.0',
              'omegaconf>=2.0.0,<3.0.0',
              'dataclasses==0.6']}

setup_kwargs = {
    'name': 'icevision',
    'version': '0.1.6',
    'description': 'Agnostic Computer Vision Framework',
    'long_description': None,
    'author': 'Lucas Goulart Vazquez',
    'author_email': 'lgvaz@airctic.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
