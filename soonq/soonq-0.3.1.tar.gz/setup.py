# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['soonq']

package_data = \
{'': ['*'], 'soonq': ['instance/*']}

setup_kwargs = {
    'name': 'soonq',
    'version': '0.3.1',
    'description': 'Subprocess-based task queue.',
    'long_description': '# SoonQ\nA subprocess-based task queue.\n\n## Introduction\nSoonQ implements a simple FIFO queue using SQLite. It was created primarily for running long simulations.\n\nAs of yet, the vision of a subprocess-based workflow has not been realized. However, the package still works as a task queue.\n\n## Installation\n`pip install soonq`\n\n## Usage\nUsers must create their own subclass of `soonq.BaseTask`. Subclasses must define a `run()` method, which contains the business logic for the task (what we care about). Input arguments to this method are restricted to being serializable via the pickle module.\n\n## Running the examples\n\nExample files are included in the examples directory. Clone SoonQ in your desired location...\n\n`C:\\desired\\location>git clone https://github.com/n8jhj/SoonQ.git`\n\n...and then navigate into the `SoonQ` directory and install it. Be careful to include the dot!\n\n`pip install .`\n\nNow run the following in two separate terminals:\n\n**Terminal 1:**\n\nRun the same script a couple times.\n\n    C:\\...\\SoonQ>python -m examples timer_task\n    Queued task: 913d56e9-a609-4b84-b937-479a94716527\n\n    C:\\...\\SoonQ>python -m examples timer_task\n    Queued task: da952424-98d9-42e1-8851-91a30924b94b\n\n    C:\\...\\SoonQ>\n\n**Terminal 2:**\n\n    C:\\...\\SoonQ>python -m examples timer_worker\n    Running task: 913d56e9-a609-4b84-b937-479a94716527\n    1/3 Sleeping 3 seconds...\n    2/3 Sleeping 3 seconds...\n    3/3 Sleeping 3 seconds...\n    Slept 9 seconds total.\n    Finished task: 913d56e9-a609-4b84-b937-479a94716527\n\n    Running task: da952424-98d9-42e1-8851-91a30924b94b\n    1/3 Sleeping 3 seconds...\n    2/3 Sleeping 3 seconds...\n    3/3 Sleeping 3 seconds...\n    Slept 9 seconds total.\n    Finished task: da952424-98d9-42e1-8851-91a30924b94b\n\n    Waiting for next task... (Ctrl + C to quit)\n\nWith the worker running, more tasks can be enqueued and will be immediately processed.\n\nPress `Ctrl + C` to quit the worker.\n\n    Quitting\n\n    C:\\...\\SoonQ>\n\n## Etymology\nThis project is named after my friend Soon-Kyoo, with whom I enjoyed countless bouts of epic ping-pong in college. People call him Q, for short.\n',
    'author': 'Nathaniel Jones',
    'author_email': 'nathaniel.j.jones@wsu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/n8jhj/SoonQ',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
