# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['splunk_otel', 'splunk_otel.cmd', 'splunk_otel.site']

package_data = \
{'': ['*']}

install_requires = \
['opentelemetry-api>=0.14b0,<0.15',
 'opentelemetry-exporter-zipkin>=0.14b0,<0.15',
 'opentelemetry-instrumentation>=0.14b0,<0.15',
 'opentelemetry-sdk>=0.14b0,<0.15']

entry_points = \
{'console_scripts': ['splk-py-trace = splunk_otel.cmd.trace:run',
                     'splk-py-trace-bootstrap = splunk_otel.cmd.bootstrap:run']}

setup_kwargs = {
    'name': 'splunk-opentelemetry',
    'version': '0.1.4',
    'description': 'The Splunk distribution of OpenTelemetry Python Instrumentation provides a Python agent that automatically instruments your Python application to capture and report distributed traces to SignalFx APM.',
    'long_description': None,
    'author': 'Splunk',
    'author_email': 'splunk-oss@splunk.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
