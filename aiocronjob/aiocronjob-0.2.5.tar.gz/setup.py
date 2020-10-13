# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aiocronjob']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.5.0,<0.6.0',
 'crontab>=0.22.8,<0.23.0',
 'fastapi>=0.55.1,<0.56.0',
 'pytz>=2020.1,<2021.0',
 'uvicorn>=0.11.5,<0.12.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=1.6.1,<2.0.0']}

setup_kwargs = {
    'name': 'aiocronjob',
    'version': '0.2.5',
    'description': 'Schedule async tasks and manage them using a REST API or WEB UI',
    'long_description': '# aiocronjob\n\n[![Join the chat at https://gitter.im/aiocronjob/community](https://badges.gitter.im/aiocronjob/community.svg)](https://gitter.im/aiocronjob/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aiocronjob?style=flat-square)\n![PyPI](https://img.shields.io/pypi/v/aiocronjob?style=flat-square)\n![PyPI - License](https://img.shields.io/pypi/l/aiocronjob?style=flat-square)\n![GitHub last commit](https://img.shields.io/github/last-commit/devtud/aiocronjob?style=flat-square)\n![PyPI - Status](https://img.shields.io/pypi/status/aiocronjob?style=flat-square)\n\nSchedule and run `asyncio` coroutines and manage them from a web interface or programmatically using the rest api.\n\n### Requires python >= 3.6\n\n### How to install\n\n```bash\npip3 install aiocronjob\n```\n\n### Usage example\n\n```python\n# examples/simple_tasks.py\n\nimport asyncio\n\nfrom aiocronjob import manager, Job\nfrom aiocronjob import run_app\n\n\nasync def first_task():\n    for i in range(20):\n        print("first task log", i)\n        await asyncio.sleep(1)\n\n\nasync def second_task():\n    for i in range(10):\n        await asyncio.sleep(1.5)\n        print("second task log", i)\n    raise Exception("second task exception")\n\n\nmanager.register(first_task, name="First task", crontab="22 * * * *")\n\nmanager.register(second_task, name="Second task", crontab="23 * * * *")\n\n\nasync def on_job_exception(job: Job, exc: BaseException):\n    print(f"An exception occurred for job {job.name}: {exc}")\n\n\nasync def on_job_cancelled(job: Job):\n    print(f"{job.name} was cancelled...")\n\n\nasync def on_startup():\n    print("The app started.")\n\n\nasync def on_shutdown():\n    print("The app stopped.")\n\n\nmanager.set_on_job_cancelled_callback(on_job_cancelled)\nmanager.set_on_job_exception_callback(on_job_exception)\nmanager.set_on_shutdown_callback(on_shutdown)\nmanager.set_on_startup_callback(on_startup)\n\nif __name__ == "__main__":\n    run_app()\n```\n\nAfter running the app, the [FastAPI](https://fastapi.tiangolo.com) server runs at `localhost:5000`.\n\n#### Web Interface\n\nOpen [localhost:5000](http://localhost:5000) in your browser:\n\n![screenshot-actionmenu](https://raw.githubusercontent.com/devtud/aiocronjob/master/examples/screenshot-actionmenu.webp)\n![screenshot-all](https://raw.githubusercontent.com/devtud/aiocronjob/master/examples/screenshot-all.webp)\n\n#### Rest API\n\nOpen [localhost:5000/docs](http://localhost:5000/docs) for endpoints docs.\n\n![EndpointsScreenshot](https://raw.githubusercontent.com/devtud/aiocronjob/master/examples/screenshot-endpoints.webp)\n\n**`curl`** example:\n \n```bash\n$ curl http://0.0.0.0:5000/api/jobs\n```\n```json\n[\n  {\n    "name": "First task",\n    "next_run_in": "3481.906931",\n    "last_status": "pending",\n    "enabled": "True",\n    "crontab": "22 * * * *",\n    "created_at": "2020-06-06T10:20:25.118630+00:00",\n    "started_at": null,\n    "stopped_at": null\n  },\n  {\n    "name": "Second task",\n    "next_run_in": "3541.904723",\n    "last_status": "error",\n    "enabled": "True",\n    "crontab": "23 * * * *",\n    "created_at": "2020-06-06T10:20:25.118661+00:00",\n    "started_at": "2020-06-06T10:23:00.000906+00:00",\n    "stopped_at": "2020-06-06T10:23:15.004351+00:00"\n  }\n]\n```\n\n### Development\n\n**Requirements**:\n- **Python** >= 3.6 and **Poetry** for backend\n- **npm** for frontend\n\nThe frontend is a separate Single Page Application (SPA), so the backend does not depend on it. It just calls the backend\'s API endpoints.\n\n#### Install backend dependencies (Python)\n\n```bash\n$ git clone https://github.com/devtud/aiocronjob.git\n\n$ cd aiocronjob\n\n$ poetry install\n```\n\n#### Run backend tests\n\n```bash\npoetry run pytest --cov -s\n```\n\n#### Run backend example\n\n```bash\npoetry run python examples/simple_tasks.py\n```\n\n`uvicorn` will run the `FastAPI` app at http://localhost:5000.\n\n#### Install frontend dependencies (React SPA)\n\nOpen another terminal tab in the project root.\n\n```bash\n$ cd src/webapp\n\n$ npm i\n```\n\n#### Run frontend tests\n\n```bash\nnpm test\n```\n\n#### Let frontend know about backend\n\nCreate `.env` file with the content from `.env.example` file to let the frontend know that the backend is running at http://localhost:5000.\n\n```bash\ncp .env.example .env\n```\n\n#### Serve frontend\n\n```bash\nnpm start\n```\n\nA `React` app starts at http://localhost:3000.\n\nYou should now be able to view the example jobs in your browser at http://localhost:3000.\n',
    'author': 'devtud',
    'author_email': 'devtud@gmail.com',
    'maintainer': 'devtud',
    'maintainer_email': 'devtud@gmail.com',
    'url': 'https://github.com/devtud/aiocronjob',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
