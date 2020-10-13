# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['skill_test']
install_requires = \
['dynabuffers==0.23.0',
 'gaia-sdk==2.0.1',
 'interstate-py==1.1.6',
 'pyyaml>=5.3.1,<6.0.0']

setup_kwargs = {
    'name': 'skill-test',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'fridayy',
    'author_email': 'benjamin.krenn@leftshift.one',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
