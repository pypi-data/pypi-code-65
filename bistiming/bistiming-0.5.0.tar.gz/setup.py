# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bistiming', 'bistiming.tests']

package_data = \
{'': ['*']}

install_requires = \
['six>=1.12,<2.0', 'tabulate>=0.8.7,<0.9.0']

setup_kwargs = {
    'name': 'bistiming',
    'version': '0.5.0',
    'description': 'A logging-friendly stopwatch and profiling tool for Python.',
    'long_description': 'BisTiming\n=========\n.. image:: https://travis-ci.com/ianlini/bistiming.svg?branch=master\n   :target: https://travis-ci.com/ianlini/bistiming\n.. image:: https://readthedocs.org/projects/pip/badge/\n   :target: https://bistiming.readthedocs.io/\n.. image:: https://img.shields.io/pypi/v/bistiming.svg\n   :target: https://pypi.org/project/bistiming/\n.. image:: https://img.shields.io/pypi/l/bistiming.svg\n   :target: https://github.com/ianlini/bistiming/blob/master/LICENSE\n.. image:: https://img.shields.io/github/stars/ianlini/bistiming.svg?style=social\n   :target: https://github.com/ianlini/bistiming\n\nA logging-friendly stopwatch and profiling tool for Python.\n\nWhen we search the stopwatch or timing module for Python on the internet, we can find a\nlot of code snippets, but none of them is powerful or convenient enough to do our daily\njobs.\nBisTiming aims at implementing all the missing functions in those code snippets and\nprevents us from reinventing the wheel.\nIt is very useful when we want to log something with some timing information or \noptimize the performance of our code.\n\nThis package is tested with Python 2.7, 3.5, 3.6 and 3.7, but might also work in other\nPython versions.\n\n.. contents::\n\nInstallation\n------------\n.. code:: bash\n\n   pip install bistiming\n\nGetting Started\n---------------\n\nBisTiming has a context manager interface that logs the running time of a code block\neasily, and it also offers a low-level API to help time multiple segments or loops of\ncode easily.\n\nSee `examples <https://github.com/ianlini/bistiming/blob/master/examples/>`_\nfor all the useful examples.\n\nContext Manager\n+++++++++++++++\n\nThe simplest way to use BisTiming is by using the context manager ``Stopwatch``\nand include the code we want to evaluate:\n\n>>> from bistiming import Stopwatch\n>>> from time import sleep\n>>> with Stopwatch("Waiting"):\n...     print("do something")\n...     sleep(0.1)\n...     print("finished something")\n...\n...Waiting\ndo something\nfinished something\n...Waiting done in 0:00:00.100330\n\nWe can use the parameter `logger` and `logging_level` to tell the stopwatch to output\nusing a logger:\n\n>>> import logging\n>>> logging.basicConfig(\n...     level=logging.DEBUG,\n...     format="[%(asctime)s] %(levelname)s: %(name)s: %(message)s")\n>>> logger = logging.getLogger(__name__)\n>>> with Stopwatch("Waiting", logger=logger, logging_level=logging.DEBUG):\n...     print("do something")\n...     sleep(0.1)\n...     print("finished something")\n...\n[2019-04-24 22:27:52,347] DEBUG: __main__: ...Waiting\ndo something\nfinished something\n[2019-04-24 22:27:52,448] DEBUG: __main__: ...Waiting done in 0:00:00.100344\n\nAnother common use case is to evaluate the running time of a specific code segment\nin a loop, we can initialize the stopwatch outside the loop, and reuse it in the loop:\n\n>>> timer = Stopwatch("Waiting")\n>>> for i in range(2):\n...     with timer:\n...         print("do something 1")\n...         sleep(0.1)\n...         print("finished something 1")\n...     print("do something 2")\n...     sleep(0.1)\n...     print("finished something 2")\n...\n...Waiting\ndo something 1\nfinished something 1\n...Waiting done in 0:00:00.100468\ndo something 2\nfinished something 2\n...Waiting\ndo something 1\nfinished something 1\n...Waiting done in 0:00:00.100440\ndo something 2\nfinished something 2\n>>> timer.split_elapsed_time\n[datetime.timedelta(microseconds=100468),\n datetime.timedelta(microseconds=100440)]\n>>> timer.get_cumulative_elapsed_time()\ndatetime.timedelta(microseconds=200908)\n\nEach item in ``split_elapsed_time`` is the running time of\nthe code segment in each iteration, and we can use\n``get_cumulative_elapsed_time()``\nto get the total running time of the code segment.\n\nLow-level API\n+++++++++++++\nThe low-level API is similar to a stopwatch in real life.\nA simple use case using the low-level API is:\n\n>>> from time import sleep\n>>> from bistiming import Stopwatch\n>>> timer = Stopwatch("Waiting").start()\n...Waiting\n>>> sleep(0.2)  # do the first step of my program\n>>> timer.split()\n...Waiting done in 0:00:00.201457\n>>> sleep(0.1)  # do the second step of my program\n>>> timer.split()\n...Waiting done in 0:00:00.100982\n\nThe context manager\n\n>>> with Stopwatch("Waiting"):\n...     sleep(0.1)\n...Waiting\n...Waiting done in 0:00:00.100330\n\nis actually equivalent to the low-level API:\n\n>>> timer = Stopwatch("Waiting").start()\n...Waiting\n>>> sleep(0.1)\n>>> timer.pause()\n>>> timer.split()\n...Waiting done in 0:00:00.100330\n\nAdvance Profiling\n+++++++++++++++++\n``MultiStopwatch`` in this package contains multiple\n``Stopwatch``, so we can use them to define each code segment\nwe want to evaluate and compare easily:\n\n>>> from time import sleep\n>>> from bistiming import MultiStopwatch\n>>> timers = MultiStopwatch(2, verbose=False)\n>>> for i in range(5):\n...    for i in range(2):\n...       with timers[0]:\n...             sleep(0.1)\n...    with timers[1]:\n...       sleep(0.1)\n...\n>>> print(timers.format_statistics())\n╒═══════════════════════════╤══════════════╤════════════╤══════════════════╕\n│ cumulative_elapsed_time   │   percentage │   n_splits │ mean_per_split   │\n╞═══════════════════════════╪══════════════╪════════════╪══════════════════╡\n│ 0:00:01.002417            │     0.666377 │         10 │ 0:00:00.100242   │\n├───────────────────────────┼──────────────┼────────────┼──────────────────┤\n│ 0:00:00.501861            │     0.333623 │          5 │ 0:00:00.100372   │\n╘═══════════════════════════╧══════════════╧════════════╧══════════════════╛\n\nDocumentation\n-------------\nThere are a lot more ways to use this package.\nSee the `documentation <https://bistiming.readthedocs.io>`_ for more information.\n',
    'author': 'Ian Lin',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://bistiming.readthedocs.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
