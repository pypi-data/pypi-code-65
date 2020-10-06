# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scanapi', 'scanapi.evaluators', 'scanapi.tree']

package_data = \
{'': ['*'], 'scanapi': ['templates/*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'click==7.1.2',
 'curlify==2.2.1',
 'jinja2==2.11.2',
 'pyyaml==5.3.1',
 'requests==2.24.0']

entry_points = \
{'console_scripts': ['scanapi = scanapi:main']}

setup_kwargs = {
    'name': 'scanapi',
    'version': '2.1.0',
    'description': 'Automated Testing and Documentation for your REST API',
    'long_description': '![](https://github.com/scanapi/design/raw/master/images/github-hero-dark.png)\n\n<p align="center">\n  <a href="https://app.circleci.com/pipelines/github/scanapi/scanapi?branch=master">\n    <img alt="CircleCI" src="https://img.shields.io/circleci/build/github/scanapi/scanapi">\n  </a>\n  <a href="https://codecov.io/gh/scanapi/scanapi">\n    <img alt="Codecov" src="https://img.shields.io/codecov/c/github/scanapi/scanapi">\n  </a>\n  <a href="https://badge.fury.io/py/scanapi">\n    <img alt="PyPI version" src="https://badge.fury.io/py/scanapi.svg">\n  </a>\n  <a href="https://spectrum.chat/scanapi">\n    <img alt="Join the community on Spectrum" src="https://withspectrum.github.io/badge/badge.svg" />\n  </a>\n</p>\n\nA library for **your API** that provides:\n\n- Automated Integration Testing\n- Automated Live Documentation\n\nGiven an API specification, written in YAML/JSON format, ScanAPI hits the specified\nendpoints, runs the test cases, and generates a detailed report of this execution - which can also\nbe used as the API documentation itself.\n\nWith almost no Python knowledge, the user can define endpoints to be hit, the expected behavior\nfor each response and will receive a full real-time diagnostic report of the API!\n\n## Contents\n\n- [Contents](#contents)\n- [Requirements](#requirements)\n- [How to install](#how-to-install)\n- [Basic Usage](#basic-usage)\n- [Documentation](#documentation)\n- [Examples](#examples)\n- [Contributing](#contributing)\n\n## Requirements\n\n- [pip][pip-installation]\n\n## How to install\n\n```bash\n$ pip install scanapi\n```\n\n## Basic Usage\n\nYou will need to write the API\'s specification and save it as a **YAML** or **JSON** file.\nFor example:\n\n```yaml\nendpoints:\n  - name: scanapi-demo # The API\'s name of your API\n    path: http://demo.scanapi.dev/api/ # The API\'s base url\n    requests:\n      - name: list_all_devs # The name of the first request\n        path: devs/ # The path of the first request\n        method: get # The HTTP method of the first request\n        tests:\n          - name: status_code_is_200 # The name of the first test for this request\n            assert: ${{ response.status_code == 200 }} # The assertion\n```\n\nAnd run the scanapi command\n\n```bash\n$ scanapi run <file_path>\n```\n\nThen, the lib will hit the specified endpoints and generate a `scanapi-report.html` file with the report results.\n\n<p align="center">\n  <img\n    src="https://raw.githubusercontent.com/scanapi/scanapi/master/images/report-print-closed.png"\n    width="700",\n    alt="An overview screenshot of the report."\n  >\n  <img\n    src="https://raw.githubusercontent.com/scanapi/scanapi/master/images/report-print-request.png"\n    width="700"\n    alt="A screenshot of the report showing the request details."\n  >\n  <img\n    src="https://raw.githubusercontent.com/scanapi/scanapi/master/images/report-print-response.png"\n    width="700",\n    alt="A screenshot of the report showing the response and test details"\n  >\n</p>\n\n## Documentation\nThe full documentation is available at [scanapi.dev][website]\n\n## Examples\nYou can find complete examples at [scanapi/examples][scanapi-examples]!\n\n\n## Contributing\n\nCollaboration is super welcome! We prepared the [Newcomers Guide][newcomers-guide] to help you in the first steps. Every little bit of help counts! Feel free to create new [GitHub issues][github-issues] and interact here.\n\nLet\'s build it together 🚀\n\n[github-issues]: https://github.com/scanapi/scanapi/issues\n[newcomers-guide]: https://github.com/scanapi/scanapi/wiki/Newcomers\n[pip-installation]: https://pip.pypa.io/en/stable/installing/\n[scanapi-examples]: https://github.com/scanapi/examples\n[website]: https://scanapi.dev\n',
    'author': 'Camila Maia',
    'author_email': 'cmaiacd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://scanapi.dev/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
