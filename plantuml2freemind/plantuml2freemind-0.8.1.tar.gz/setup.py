# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['plantuml2freemind',
 'plantuml2freemind.generators',
 'plantuml2freemind.parsers']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.3.0,<20.0.0',
 'cleo>=0.8.1,<0.9.0',
 'pyyaml>=5.3.1,<6.0.0',
 'typing-extensions>=3.7.4,<4.0.0']

entry_points = \
{'console_scripts': ['plantuml2freemind = plantuml2freemind.cli:main']}

setup_kwargs = {
    'name': 'plantuml2freemind',
    'version': '0.8.1',
    'description': 'Converts plantuml mindmaps to freemind .mm files',
    'long_description': "# plantuml2freemind\n[![Downloads](https://pepy.tech/badge/plantuml2freemind)](https://pepy.tech/project/plantuml2freemind)\n\nConverts plantuml mindmaps to FreeMind .mm files (and few other formats).\n\nCreated especially for [Teamlead Roadmap](https://github.com/tlbootcamp/tlroadmap) project, which stores and\nmaintains a big community-driven roadmap in a mindmap. It's very convenient to have text plantuml as a source\nformat and generate other required formats from it.\n\n## Prerequisites\n\n- python >= 3.7 \n\n## Installation\n\n`pip install plantuml2freemind`\n\n## Usage\n\n`plantuml2freemind --help` or `python -m plantuml2freemind --help`\n\nConvert example in one command:\n\n`plantuml2freemind convert examples/small_teamlead_roadmap.puml output.mm`\n\n## Contributing\nPull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.\n\n### Local development\nThe project uses poetry as a dependency management tool. For local development convenient way to installing and\nrunning project is using `poetry install`. Please, use [>=1.0.0 version](https://pypi.org/project/poetry/#history) of\npoetry even if it is a beta-version.\n\nPoetry automatically creates venv (or uses already activated venv) and install all requirements to it and the project\nitself as `editable` . After installing you can run project as a typical python script \n(`python plantuml2freemind/cli.py --help`) or as python's package entry_point (`plantuml2freemind --help`)\n\nTIP: Use `poetry shell` or `poetry run` before running commands: they activate venv. If you want to connect venv to\nyour IDE, use `poetry env list --full-path`\n\n## License\n[MIT](https://choosealicense.com/licenses/mit/)\n",
    'author': 'Boger',
    'author_email': 'kotvberloge@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/b0g3r/plantuml2freemind',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
