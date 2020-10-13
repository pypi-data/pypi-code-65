# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['glennopt',
 'glennopt.base_classes',
 'glennopt.helpers',
 'glennopt.nsga3',
 'glennopt.sode',
 'glennopt.test_functions',
 'glennopt.test_functions.KUR.parallel',
 'glennopt.test_functions.KUR.parallel.Evaluation',
 'glennopt.test_functions.KUR.parallel_machine_file',
 'glennopt.test_functions.KUR.parallel_machine_file.Evaluation',
 'glennopt.test_functions.KUR.serial',
 'glennopt.test_functions.KUR.serial.Evaluation',
 'glennopt.test_functions.ProbePlacement.serial',
 'glennopt.test_functions.ProbePlacement.serial.Evaluation',
 'glennopt.test_functions.Rosenbrock.serial',
 'glennopt.test_functions.Rosenbrock.serial.Evaluation']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.3.1,<4.0.0', 'numpy', 'pandas', 'psutil']

setup_kwargs = {
    'name': 'glennopt',
    'version': '1.0.2',
    'description': 'Multi and single objective optimization tool for cfd/computer simulations.',
    'long_description': None,
    'author': 'Paht Juangphanich',
    'author_email': 'paht.juangphanich@nasa.gov',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
