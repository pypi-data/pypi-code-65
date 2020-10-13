# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['delatore',
 'delatore.configuration',
 'delatore.outputs',
 'delatore.outputs.alerta',
 'delatore.outputs.telegram',
 'delatore.sources']

package_data = \
{'': ['*'],
 'delatore.configuration': ['resources/*'],
 'delatore.outputs.telegram': ['messages/*'],
 'delatore.sources': ['resources/*']}

install_requires = \
['aiodns>=2.0.0,<3.0.0',
 'aiogram==2.9.2',
 'aiohttp-socks>=0.3.4,<0.4.0',
 'aiohttp>=3.6.2,<4.0.0',
 'alerta>=7.4.4,<8.0.0',
 'apubsub>=0.2.5,<0.3.0',
 'influxdb==5.2.3',
 'jinja2>=2.11.2,<3.0.0',
 'jsonschema[format]>=3.2.0,<4.0.0',
 'ocomone>=0.4.3,<0.5.0',
 'pyyaml-typed>=0.1.0,<0.2.0',
 'rfc3339-validator>=0.1.2,<0.2.0']

setup_kwargs = {
    'name': 'delatore',
    'version': '0.5.1',
    'description': 'Bot for CSM jobs notifications in telegram and alerta',
    'long_description': 'Delatore\n========\n\n| |Build Status|\n| |Zuul|\n| |codecov|\n| |PyPI version|\n| |GitHub|\n\nMonitor and report status of customer service monitoring scenarios\n\nBot commands\n------------\n\nTelegram bot accepts following commands:\n\n``/status``\n~~~~~~~~~~~\n\nBot reply to the message with last status(-es) retrieved from given\nsource\n\nStatus has following syntax:\n\n``/status <source> [detailed_source] [history_depth]``\n\nIf some argument contains spaces, it should be surrounded by quotes,\neither ``\'...\'`` or ``"..."``\n\nAWX Source\n^^^^^^^^^^\n\nStatus command for AWX source has following syntax:\n\n``/status awx [template_name] [history_depth]``\n\nExamples:\n\n-  ``/status awx`` — return last job status for all *scenarios*\n-  ``/status awx \'Buld test host\'`` — return last job status for AWX\n   template which called \'Buld test host\'\n-  ``/status awx \'Scenario 1.5\' 3`` — return status of last 3 jobs for\n   AWX template which called ``Scenario 1.5``\n\n.. |Build Status| image:: https://travis-ci.org/opentelekomcloud-infra/delatore.svg?branch=master\n   :target: https://travis-ci.org/opentelekomcloud-infra/delatore\n.. |codecov| image:: https://codecov.io/gh/opentelekomcloud-infra/delatore/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/opentelekomcloud-infra/delatore\n.. |PyPI version| image:: https://img.shields.io/pypi/v/delatore.svg\n   :target: https://pypi.org/project/delatore/\n.. |GitHub| image:: https://img.shields.io/github/license/opentelekomcloud-infra/delatore\n.. |Zuul| image:: https://zuul-ci.org/gated.svg\n',
    'author': 'OTC customer service monitoring team',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/opentelekomcloud-infra/delatore',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
