# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['amqpeek']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0',
 'click>=7.1.2,<8.0.0',
 'pika>=1.1.0,<2.0.0',
 'slacker>=0.14.0,<0.15.0']

entry_points = \
{'console_scripts': ['amqpeek = amqpeek.cli:main']}

setup_kwargs = {
    'name': 'amqpeek',
    'version': '0.0.7',
    'description': 'A flexible RMQ monitor that keeps track of RMQ, notifying you over multiple channels when connections cannot be made, queues have not been declared, and when queue lengths increase beyond specified limits.',
    'long_description': '[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/C0C826VYD)\n\n![Tests](https://github.com/steveYeah/amqpeek/workflows/Tests/badge.svg)\n![Coverage](https://github.com/steveYeah/amqpeek/workflows/Coverage/badge.svg)\n![Release Drafter](https://github.com/steveYeah/amqpeek/workflows/Release%20Drafter/badge.svg)\n![TestPyPi](https://github.com/steveYeah/amqpeek/workflows/TestPyPi/badge.svg)\n![Release](https://github.com/steveYeah/amqpeek/workflows/Release/badge.svg)\n\n[![Codecov](https://codecov.io/gh/steveYeah/amqpeek/branch/master/graph/badge.svg)](https://codecov.io/gh/steveYeah/amqpeek)\n[![PyPI](https://img.shields.io/pypi/v/amqpeek.svg)](https://pypi.org/project/amqpeek/)\n\nAMQPeek\n=======\n\n> A flexible RMQ monitor that keeps track of RMQ, notifying you over\n> multiple channels when connections cannot be made, queues have not\n> been declared, and when queue lengths increase beyond specified\n> limits.\n\nSupport OSS, and me :)\n----------------------\n\nIf you find this project useful, please feel free to [buy me a coffee](https://ko-fi.com/steveyeah)\n\nInstall\n-------\n\n``` {.sourceCode .shell}\n$ pip install amqpeek\n```\n\nOnce installed, you can then setup AMQPeek to suit your needs by editing\nthe configuration file\n\nCreate configuration file\n-------------------------\n\nTo create a base configuration file:\n\n``` {.sourceCode .shell}\n$ amqpeek --gen_config\n```\n\nThis will create a file called `amqpeek.yaml` in your current directory.\nHere you can setup your connection details for RMQ, define queues you\nwish to monitor and define the notifier channels you wish to use. Edit\nthis file to suit your needs\n\nRunning\n-------\n\nlisting all options:\n\n``` {.sourceCode .shell}\n$ amqpeek --help\n```\n\nRun AMQPeek with no arguments: This runs the monitoring script once and\nthen exits out (useful when running AMQPeek as a Cron job)\n\n``` {.sourceCode .shell}\n$ amqpeek\n```\n\nRun AMQPeek with an interval: This monitors RMQ, running the tests every\n10 minutes in a continuous loop (useful when running AMQPeek under\nSupervisor or something similar)\n\n``` {.sourceCode .shell}\n$ amqpeek --interval 10\n```\n\nYou can also specify the location of a configuration file to use instead\nof the default location of your current directory\n\n``` {.sourceCode .shell}\n$ amqpeek --config config.yaml\n```\n\nNotification channels\n---------------------\n\nAMQPeek supports multiple notification channels.\n\nCurrently supported channels:\n\n-   Slack\n-   Email (SMTP)\n\nThese are controlled via the configuration file, under notifiers. You\ncan mix and match the notifiers you wish to use, and you can have\nmultiples of the same notifier types.\n',
    'author': 'steveYeah',
    'author_email': 'hutchinsteve@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/steveYeah/amqpeek',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
