# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['convenient_ai',
 'convenient_ai.nlp',
 'convenient_ai.nlp.__api__',
 'convenient_ai.nlp.__common__',
 'convenient_ai.nlp.__common__.io',
 'convenient_ai.nlp.spacy',
 'convenient_ai.nlp.spacy.custom',
 'convenient_ai.nlp.spacy.types']

package_data = \
{'': ['*']}

extras_require = \
{'spacy': ['spacy>=2.3,<3.0']}

entry_points = \
{'console_scripts': ['release = poetry_scripts:release',
                     'test = poetry_scripts:test']}

setup_kwargs = {
    'name': 'convenient-ai',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'leftshift one',
    'author_email': 'devs@leftshift.one',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
