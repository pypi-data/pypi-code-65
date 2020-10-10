# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyxvis',
 'pyxvis.features',
 'pyxvis.geometry',
 'pyxvis.io',
 'pyxvis.learning',
 'pyxvis.processing',
 'pyxvis.processing.helpers',
 'pyxvis.simulation']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.3.2,<4.0.0',
 'numpy<1.19',
 'opencv-contrib-python>=4.4.0,<5.0.0',
 'opencv-python>=4.4.0,<5.0.0',
 'pandas>=1.1.2,<2.0.0',
 'pybalu>=0.2.9,<0.3.0',
 'pyqt5>=5.15.1,<6.0.0',
 'scikit-image>=0.17.2,<0.18.0',
 'scikit-learn>=0.23.2,<0.24.0',
 'scipy>=1.5.2,<2.0.0',
 'tensorflow>=2.3.1,<3.0.0']

setup_kwargs = {
    'name': 'pyxvis',
    'version': '0.1.0a1',
    'description': 'Python package for Xvis toolbox',
    'long_description': '# py-XVis\n\nPython implementation for XVis Toolbox release with the book Computer Vision for X-Ray Testing. Originally implemented \nin Matlab by Domingo Mery for the first edition of the book. This package is part of the second edition of the book \nComputer Vision for X-Ray Testing (November 2020).\n\n\n# Requirements\n\n- Python 3.6 or higher\n- Numpy\n- Scipy\n- Matplotlib\n- OpenCV 4.0 or higher\n\n\n# Instalation\nThe package is part of the Python Index (PyPi). Installation is available by pip:\n\n`pip install pyxivs`\n',
    'author': 'Christian Pieringer',
    'author_email': '8143906+cpieringer@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
