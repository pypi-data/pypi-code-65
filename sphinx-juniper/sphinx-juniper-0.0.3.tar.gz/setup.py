# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sphinx_juniper']

package_data = \
{'': ['*'], 'sphinx_juniper': ['_static/*']}

install_requires = \
['sphinx>=2.0']

setup_kwargs = {
    'name': 'sphinx-juniper',
    'version': '0.0.3',
    'description': 'Convert Jupyter Notebooks into runnable HTML files with Juniper (https://github.com/ines/juniper).',
    'long_description': '# sphinx-juniper\nIntegrate interactive code blocks into your documentation with [Juniper](https://github.com/ines/juniper) and [Binder](https://mybinder.org).\n\n## Install\n\nTo install `sphinx-juniper` first clone and install it:\n\n```\npip install sphinx-juniper\n```\n\nThen, add it to your Jupyter Book\'s `_config.yml` file:\n\n(to use all default values)\n```\nsphinx:\n  extra_extensions:\n    - sphinx_juniper\n  config:\n    juniper: true\n```\n\nTo override any/all defaults:\n```\nsphinx:\n  extra_extensions:\n    - sphinx_juniper\n  config:\n    juniper:\n      url: https://mybinder.org  # BinderHub instance\n      repo: ashtonmv/python_binder  # Github repository for Binder image\n      theme: monokai  # Styling (only monokai and material supported for now)\n      isolateCells: false  # Whether to share variables between cells\n      useStorage: true  # Cache the kernel connection between page loads\n      ...\n      etc.\n      ...\n```\n\nSimilar to BinderHub links and Colab links, sphinx-juniper only acts on\nIpython Notebooks included in your documentation! It adds a button to the "launch_buttons" (the one with a rocket on it) dropdown menu for these pages at\nthe top. Clicking this button will start the connection to the kernel you\'ve\nconfigured based on the settings in _config.yml above.',
    'author': 'Michael Ashton',
    'author_email': 'ashtonmv@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ashtonmv/sphinx-juniper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
