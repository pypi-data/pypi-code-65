# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['codustry',
 'codustry.models',
 'codustry.protocals',
 'codustry.rules',
 'codustry.rules.etiquette']

package_data = \
{'': ['*']}

install_requires = \
['autoname>=0.1.2,<0.2.0',
 'avajana>=0.4.1,<0.5.0',
 'halo>=0.0.30,<0.0.31',
 'pydantic>=1.6.1,<2.0.0']

setup_kwargs = {
    'name': 'codustry',
    'version': '0.1.0',
    'description': 'codustry protocals',
    'long_description': '| Title   | The Ultimate Purpose of Codustry |\n| ------- | ------------------- |\n| Author  | Nutchanon Ninyawee  |\n| Status  | Draft               |\n| Type    | None                |\n| Created | 24 Nov 2019                |\n\n\n# CEP -1 -- The Ultimate Purpose of Codustry (cep negative one)\n\nwe code & maintain millennium projects.\n\nCodustry\'s Corporate Mission Statement:\n"To Question, Strike and Maintain Digital World\'s Balances. We engineer our products, services, and infrastructures in a circular, dynamic, millennium-long fashion."\n\nCodustry\'s Corporate Vision Statement:\n"To be Earth\'s most humane company, where stakeholders wish to do business with us for 1000+ years."\n\n',
    'author': 'Nutchanon Ninyawee',
    'author_email': 'nutchanon@codustry.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/codustry/ceps',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
