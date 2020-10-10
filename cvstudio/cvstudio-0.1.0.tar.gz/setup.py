# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cvstudio',
 'cvstudio.constants',
 'cvstudio.contrib',
 'cvstudio.contrib.dextr',
 'cvstudio.core',
 'cvstudio.dao',
 'cvstudio.decor',
 'cvstudio.extra',
 'cvstudio.schemas',
 'cvstudio.util',
 'cvstudio.view',
 'cvstudio.view.forms',
 'cvstudio.view.forms.dataset_form',
 'cvstudio.view.forms.label_form',
 'cvstudio.view.forms.repo_form',
 'cvstudio.view.widgets',
 'cvstudio.view.widgets.common',
 'cvstudio.view.widgets.double_slider',
 'cvstudio.view.widgets.gallery',
 'cvstudio.view.widgets.image_button',
 'cvstudio.view.widgets.image_viewer',
 'cvstudio.view.widgets.labels_tableview',
 'cvstudio.view.widgets.lateral_menu',
 'cvstudio.view.widgets.loading_dialog',
 'cvstudio.view.widgets.models_treeview',
 'cvstudio.view.widgets.response_grid',
 'cvstudio.view.widgets.switch_button',
 'cvstudio.view.widgets.top_bar',
 'cvstudio.view.windows',
 'cvstudio.view.windows.main_window',
 'cvstudio.view.wizard',
 'cvstudio.view.wizard.model_wizard',
 'cvstudio.vo']

package_data = \
{'': ['*'],
 'cvstudio': ['assets/icons/cvstudio/*',
              'assets/icons/dark/*',
              'assets/icons/gray/*',
              'assets/icons/light/*',
              'assets/styles/cvstudio/*',
              'assets/styles/dark/*',
              'assets/styles/gray/*',
              'assets/styles/light/*',
              'data/*',
              'models/.gitignore']}

install_requires = \
['dask[complete]>=2.30.0,<3.0.0',
 'hurry.filesize>=0.9,<0.10',
 'hurry>=1.1,<2.0',
 'imutils>=0.5.3,<0.6.0',
 'mako>=1.1.3,<2.0.0',
 'marshmallow>=3.8.0,<4.0.0',
 'matplotlib>=3.3.2,<4.0.0',
 'more_itertools>=8.5.0,<9.0.0',
 'numpy>=1.19.2,<2.0.0',
 'opencv-python==4.1.0.25',
 'pandas>=1.1.3,<2.0.0',
 'peewee>=3.13.3,<4.0.0',
 'pyqt5>=5.15.1,<6.0.0']

entry_points = \
{'console_scripts': ['cvstudio = cvstudio.__main__:main']}

setup_kwargs = {
    'name': 'cvstudio',
    'version': '0.1.0',
    'description': 'Computer vision projects annotation tools',
    'long_description': None,
    'author': 'haruiz',
    'author_email': 'henryruiz22@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
