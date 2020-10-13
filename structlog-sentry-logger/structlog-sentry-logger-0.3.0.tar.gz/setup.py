# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['structlog_sentry_logger']

package_data = \
{'': ['*']}

install_requires = \
['gitpython>=3.1.7,<4.0.0',
 'python-dotenv>=0.14.0,<0.15.0',
 'sentry-sdk>0.17.0',
 'structlog-sentry>=1.2.2,<2.0.0',
 'structlog>=20.1.0,<21.0.0']

setup_kwargs = {
    'name': 'structlog-sentry-logger',
    'version': '0.3.0',
    'description': 'A multi-purpose, pre-configured [`structlog`](https://www.structlog.org/en/stable/) logger with (optional) [Sentry](https://sentry.io/welcome/) integration via [`structlog-sentry`](https://github.com/kiwicom/structlog-sentry).',
    'long_description': 'Structlog-Sentry-Logger\n==============================\n\nA multi-purpose, pre-configured [`structlog`](https://www.structlog.org/en/stable/) logger\nwith (optional) [Sentry](https://sentry.io/welcome/) integration\nvia [`structlog-sentry`](https://github.com/kiwicom/structlog-sentry).\n\n##### Benefits:\n1. Makes logging as easy as using print statements, but prettier and less smelly!\n2. Highly opinionated! There are only two (2) distinct configurations. \n3. Structured logs in JSON format means they are ready to be ingested by many\nfavorite log analysis tools!\n\nSave your tears for what you do best: writing fancy computer mumbo jumbo to\nmake the world a better place!  \n\n\nUsage\n==============================\nPure `structlog` Logging (Without Sentry)\n------------\nAt the top of your Python module, import and instantiate the logger:\n```python\nfrom structlog_sentry_logger import logger\nLOGGER = logger.get_logger()\n```\nNow anytime you want to print anything, don\'t. Instead do this:\n```python\nLOGGER.info("Information that\'s useful for future me and others", extra_field="extra_value")\n```\n###### Note: all the regular [Python logging levels](https://docs.python.org/3/library/logging.html#levels) are supported.\n```\n{\n    "event": "Information that\'s useful for future me and others",\n    "extra_field": "extra_value",\n    "level": "info",\n    "logger": "<input>",\n    "timestamp": "2020-09-25 17:21:26",\n}\n```\n\nWith `structlog`, you can even incorporate custom messages in your exception handling:\n```python\nimport uuid\n\nfrom structlog_sentry_logger import logger\nLOGGER = logger.get_logger()\n\ncurr_user_logger = LOGGER.bind(uuid=uuid.uuid4().hex)  # LOGGER instance with bound UUID\ntry:\n    curr_user_logger.warn("A dummy error for testing purposes is about to be thrown!")\n    assert False\nexcept AssertionError as err:\n    err_msg = ("I threw an error on purpose for this example!\\n"\n               "Now throwing another that explicitly chains from that one!")\n    curr_user_logger.exception(err_msg)\n    raise RuntimeError(err_msg) from err\n```\n\n```\n{\n    "event": "A dummy error for testing purposes is about to be thrown!",\n    "level": "warning",\n    "logger": "<input>",\n    "timestamp": "2020-09-25 17:19:02",\n    "uuid": "68f595440e69478a97a26b002f9cbf44",\n}\n{\n    "event": "I threw an error on purpose for this example!\\nNow throwing another that explicitly chains from that one!",\n    "exception": \'Traceback (most recent call last):\\n  File "<input>", line 8, in <module>\\nAssertionError\',\n    "level": "error",\n    "logger": "<input>",\n    "timestamp": "2020-09-25 17:19:02",\n    "uuid": "68f595440e69478a97a26b002f9cbf44",\n}\nTraceback (most recent call last):\n  File "<input>", line 8, in <module>\nAssertionError\nThe above exception was the direct cause of the following exception:\nTraceback (most recent call last):\n  File "<input>", line 13, in <module>\nRuntimeError: I threw an error on purpose for this example!\nNow throwing another that explicitly chains from that one!\n```\nSentry Integration\n------------\nExport your [Sentry DSN](https://docs.sentry.io/platforms/python/#configure) \ninto your local environment. \n\n- An easy way to do this is to put it into a local `.env` file and use \n`python-dotenv` to populate your environment:\n ```shell script\n# On the command line:\nSENTRY_DSN=YOUR_SENTRY_DSN\n echo "SENTRY_DSN=${SENTRY_DSN}" > .env\n```\n```python\n# In your Python code, prior to instantiating the logger:\nfrom dotenv import find_dotenv, load_dotenv\nload_dotenv(find_dotenv())\n```\n\nOutput: Formatting & Storage\n==============================\nThe default behavior is to stream JSON logs directly to the standard output\nstream [like a proper 12 Factor App](https://12factor.net/logs).\n\nFor local development, it often helps to prettify logging to stdout and save\nJSON logs to a `.logs` folder at the root of your project directory. To enable\nthis behavior, set the following environment variable:\n```bash\nCI_ENVIRONMENT_SLUG=dev-local\n```\nIn doing so, with our previous exception handling example we would get:\n\n<img src=".static/Output_Formatting_example.png">\n\nSummary\n==============================\nThat\'s it. Now no excuses.\nGet out there and program with pride knowing no one\nwill laugh at you in production! For not logging properly, that is. You\'re on your own\nfor that other [observability](https://devops.com/metrics-logs-and-traces-the-golden-triangle-of-observability-in-monitoring/) stuff.\n\nFurther Reading\n==============================\n<img src="https://www.structlog.org/en/stable/_static/structlog_logo_small.png" width="200">\n\n### [`Structlog`](https://www.structlog.org/en/stable/#): Structured Logging for Python\n\n<img src="https://camo.githubusercontent.com/2dfeafbee0904d6df16ddf7200993dace1629e60/68747470733a2f2f73656e7472792d6272616e642e73746f726167652e676f6f676c65617069732e636f6d2f73656e7472792d6c6f676f2d626c61636b2e706e67" width="400">\n\n### [`Sentry`](https://sentry.io/welcome/): Monitor and fix crashes in realtime.\n\n### [`structlog-sentry`](https://github.com/kiwicom/structlog-sentry): Provides the `structlog` `SentryProcessor` for `Sentry` integration.\n',
    'author': 'Teo Zosa',
    'author_email': 'teo@sonosim.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://gitlab.sonosim.local/CorSAIR/utils/structlog-sentry-logger',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
