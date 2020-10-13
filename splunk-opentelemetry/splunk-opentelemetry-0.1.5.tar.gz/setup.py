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
    'version': '0.1.5',
    'description': 'The Splunk distribution of OpenTelemetry Python Instrumentation provides a Python agent that automatically instruments your Python application to capture and report distributed traces to SignalFx APM.',
    'long_description': "# Splunk Otel Python\n\nThe Splunk distribution of OpenTelemetry Python Instrumentation provides a Python agent that automatically instruments your Python application to capture and report distributed traces to SignalFx APM.\n\nThis Splunk distribution comes with the following defaults:\n\n  * B3 context propagation.\n  * Zipkin exporter configured to send spans to a locally running SignalFx Smart Agent (http://localhost:9080/v1/trace).\n  * Unlimited default limits for configuration options to support full-fidelity traces.\n\n## Getting Started\n\n### 1. Install the package\n\nThis will install splunk-opentelemetry and any other packages required to start tracing a Python application.\n\n```\npip install splunk-opentelemetry\n```\n\n### 2. Detect and install instrumentations\n\nThis will detect installed packages in your active Python environment and install the relevant instrumentation\npackages.\n\n```\nsplk-py-trace-bootstrap\n```\n\n#### Alternative: List requirements instead of installing them\n\nThe `splk-py-trace-bootstrap` command can optionally print out the list of packages it would install if you chose.\nIn order to do so, pass `-a=requirements` CLI argument to it. For example,\n\n```\nsplk-py-trace-bootstrap -a requirements\n```\n\nWill output something like the following:\n\n```\nopentelemetry-instrumentation-falcon>=0.14b0\nopentelemetry-instrumentation-jinja2>=0.14b0\nopentelemetry-instrumentation-requests>=0.14b0\nopentelemetry-instrumentation-sqlite3>=0.14b0\nopentelemetry-exporter-zipkin>=0.14b0\n```\n\nYou can pipe the output of this command to append the new packages to your requirements.txt file or to something like `poetry add`.\n\n### 3. Automatically trace your python application\n\nWith all the packages required to trace and instrument your application installed, you can start your application using the `splk-py-trace`\ncommand to auto-instrument and auto-configure tracing. For example, if you usually start your Python application as `python main.py --port=8000`,\nyou'd have to change it to the following command:\n\n```\nsplk-py-trace python main.py --port=8000\n```\n\n#### Alternative: Instrument and configure by adding code\n\nIf you cannot use `splk-py-trace` command, you can also add a couple of lines of code to your Python application to acheive the same result.\n\n```python\nfrom splunk_otel.tracing import start_tracing\n\nstart_tracing()\n\n# rest of your python application's entrypoint script\n```\n\n##### Manually configuring Celery workers\n\nCelery workers must call the `start_tracing()` function after worker process is initialized. If you are trying to trace a celery worker,\nyou must use Celery's `celery.signals.worker_process_init` signal to start tracing. For example:\n\n```python\nfrom splunk_otel.tracing import start_tracing\nfrom celery.signals import worker_process_init\n\n@worker_process_init.connect(weak=False)\ndef on_worker_process_init(*args, **kwargs):\n    start_tracing()\n\n# rest of your python application's entrypoint script\n```\n\nThis is completely automated when using the `splk-py-trace` command to start Python applications and is only required when instrumenting\nby hand.\n\n\n## Development\n\n### Bootstraping \n\n#### Install Poetry\n\nThis project uses poetry to manage dependencies and the package. Follow the instructions here to install Poetry on your system: https://python-poetry.org/docs/#installation\n\n#### Install dependencies\n\nOnce poetry is installed and available run the following command to install all package required for local development.\n\n```\nmake dep\n```\n\n### Testing in a local project\n\nIn order to install and test the package in a local test project, we'll need to generate a setup.py file and then install an editable version of the package in the test project's environment. Assuming the test project environment lives at `/path/to/test/project/venv`, the following steps will install an editable version of package in the test project.\n\n```\nmake develop\ncd dev\n. /path/to/test/project/venv/bin/activate\npython setup.py develop\n```\n\nThis will install an editable version of the package in the test project. Any changes made to the library will automatically reflect in the test project without the need to install the package again.\n",
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
