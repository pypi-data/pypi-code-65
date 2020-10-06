# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['web_youtube_dl', 'web_youtube_dl.app']

package_data = \
{'': ['*'], 'web_youtube_dl.app': ['static/*', 'templates/*']}

install_requires = \
['Werkzeug>=1.0.1,<2.0.0',
 'aiofiles>=0.5.0,<0.6.0',
 'cachetools>=4.1.1,<5.0.0',
 'fastapi>=0.61.0,<0.62.0',
 'janus>=0.5.0,<0.6.0',
 'jinja2>=2.11.2,<3.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'uvicorn>=0.11.8,<0.12.0',
 'youtube-dl>=2020.7.28,<2021.0.0']

entry_points = \
{'console_scripts': ['web-youtube-dl = web_youtube_dl.app.main:run_app',
                     'web-youtube-dl-cli = '
                     'web_youtube_dl.app.youtube_dl_helpers:cli_download']}

setup_kwargs = {
    'name': 'web-youtube-dl',
    'version': '0.1.4',
    'description': 'A web version of youtube-dl',
    'long_description': '.. image:: https://badge.fury.io/py/web-youtube-dl.svg\n    :target: https://badge.fury.io/py/web-youtube-dl\n    :alt: PyPi Package\n\n.. image:: https://img.shields.io/pypi/pyversions/web-youtube-dl\n    :target: https://pypi.org/project/web-youtube-dl/\n    :alt: Compatible Python Versions\n\n\nAbout\n=====\n\nThis is a project that builds on youtube-dl to provide a simple web-interface \nfor downloading audio from Youtube. It\'s primary purpose is to provide a LAN \nHTTP accessible method of saving audio to a local device.\n\nThis project is built using python\'s asyncio libraries and packages include \nFastAPI, janus, and uvicorn. It\'s also an example of how to work with youtube-dl\'s \npython sdk and enable asynchronous downloads in the context of a web-app. \n\nFiles are downloaded using an API endpoint and then retrived from the application\'s \nstatic files directory using Javascript\'s fetch API. Download progress is presented \nvia a websocket connection.\n\n\nInstallation\n============\n\n.. code-block:: bash\n\n    pip install web-youtube-dl\n\n\nRunning\n=======\n\nCLI\n---\n\nInstalling this project will give you access to two CLI tools, each with a separate \npurpose:\n\n* | **web-youtube-dl-cli**\n  | Useful for simply downloading the highest possible quality \n  | audio of a song. Simply provide the URL and an .mp3 will be downloaded to that \n  | same directory\n\n* | **web-youtube-dl**\n  |  Useful for running the web service on the local machine. It will \n  |  listen to all local network connections on port 5000 (or whatever port is defined \n  |  in the environment variable *YT_DOWNLOAD_PORT*).\n\n\nDocker\n------\n\nThis project can optionally be run and managed as a Docker container.\n\nBuild the Docker image\n^^^^^^^^^^^^^^^^^^^^^^\n\n.. code-block:: bash\n\n    docker build . -t  web-youtube-dl:latest --force-rm\n\nOr, using the project\'s Makefile\n\n.. code-block:: bash\n\n    make container\n\nRun the service\n^^^^^^^^^^^^^^^\n\nWhen running the service via Docker, you can configure where it stores downloaded \nsongs by default and the port the service listens on by setting the appropriate \nenvironment variables.\n\nTo configure the port, set the environment variable *YT_DOWNLOAD_PORT* to some \nother numerical value.\n\nTo configure the download path, set the environment variable *YT_DOWNLOAD_PATH* \nto some other filesystem path. Note that an unprivileged user must have access \nto writing to this location. By default, this is set to *tmp* and does not \nreally need to be changed.\n\n.. code-block:: bash\n\n    docker-compose up -d\n\nOr, using the project\'s Makefile\n\n.. code-block:: bash\n\n    make compose\n\nKnown Issues\n============\n\nBackend issues if a single user hits submit multiple times\n  - "raise RuntimeError("Response content longer than Content-Length")"\n\nShould probably build in some websocket Acking during broadcast',
    'author': 'Uriel Mandujano',
    'author_email': 'uriel.mandujano14@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
