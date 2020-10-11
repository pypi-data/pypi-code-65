# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jure']

package_data = \
{'': ['*']}

install_requires = \
['jupytext>=1.5.2,<2.0.0',
 'loguru>=0.5.2,<0.6.0',
 'pytest>=6.0.1,<7.0.0',
 'selenium>=3.141.0,<4.0.0',
 'watchdog>=0.10.3,<0.11.0']

entry_points = \
{'console_scripts': ['jure = jure.main:main']}

setup_kwargs = {
    'name': 'jure',
    'version': '0.2.0',
    'description': 'An utility that extends Jupytext. Allows to auto-refresh browser when source file is changed.',
    'long_description': "# Jupyter Browser Reload\n\nFlow-saving tool that automatically reloads Jupyter Notebook in a browser\nwhen its source .py file is changed and executes changed cells.\n\nIt uses\n* [Jupytext](https://github.com/mwouts/jupytext) - to synchronize .ipynb and .py files\n* [Watchdog](https://github.com/gorakhargosh/watchdog) - to watch for .py file changes\n* [Selenium](https://github.com/SeleniumHQ/selenium) - to have a full control over a browser with opened Jupyter Notebook \n\n## Why Jure\nJupytext is a great tool that for instance allows user to benefit from static code analysis of Jupyter Notebooks. However I always struggled with this workflow: after each edit of .py file I needed to manually reload browser and execute changed cells.\n\n![standard](assets/standard.gif)\n\nJure automatically reloads browser on each .py file change, so it would instantly show actual notebook content. Additionally it scrolls to last changed cell and executes it. \n \n![with jure](assets/with_jure.gif)\n\n\n## Installation\nThe most non-trivial part is install ChromeDriver on you computer, here's [sample link for Ubuntu](https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/) for reference.\nAfter that it's simply\n```\npip install jure\n```\n\n## Usage\nFirst, you need to sync your .ipynb file with .py with Jupytext, see [official manual](https://github.com/mwouts/jupytext#using-jupytext).\n\nThen launch a Jupyter Notebook server (`jupyter notebook ...`).\n\nThen run\n```bash\njure --token=[TOKEN] --jupyter_root_dir=[ROOT_DIR] --notebook_path=[NOTEBOOK_PATH]\n```\nWhere `[TOKEN]` as an access token which is required to access Jupyter Notebook from browser, `[ROOT_DIR]` is a path to directory from which `jupyter notebook ...` command was executed and `[NOTEBOOK_PATH]` is a path to the notebook .ipynb file you'll work with.\n\n## Limitations\nThis is an experimental and unstable product, any issues, suggestions, feature requests and PRs are appreciated. Current problems:\n\n* Only Google Chrome web browser is supported\n* Selenium might be inconvenient\n* No password auth / remote notebook hosts\n* Only last changed cell is executed, also first cell with imports is always executed\n* In some rare cases user needs to reload browser tab manually\n* For large notebooks page reload might be too slow (tough one)",
    'author': 'Dmitry Lipin',
    'author_email': 'd.lipin@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
