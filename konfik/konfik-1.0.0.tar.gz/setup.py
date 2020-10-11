# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['konfik']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0',
 'python-dotenv>=0.14.0,<0.15.0',
 'rich>=8.0.0,<9.0.0',
 'toml>=0.10.1,<0.11.0']

entry_points = \
{'console_scripts': ['konfik = konfik.main:deploy_cli']}

setup_kwargs = {
    'name': 'konfik',
    'version': '1.0.0',
    'description': 'The Strangely Familiar Config Parser',
    'long_description': '<div align="center">\n\n<img src="https://user-images.githubusercontent.com/30027932/95400681-0a8b1f00-092d-11eb-9868-dfa8ff496565.png" alt="konfik-logo">\n\n<strong>>> <i>The Strangely Familiar Config Parser</i> <<</strong>\n<br></br>\n![Codecov](https://img.shields.io/codecov/c/github/rednafi/konfik?color=pink&style=flat-square&logo=appveyor)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square&logo=appveyor)](https://github.com/python/black)\n[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square&logo=appveyor)](./LICENSE)\n</div>\n\n\n## 📖 Description\n\nKonfik is a simple configuration parser that helps you access your TOML or DOTENV config variables using dot (.) notation. This enables you to do this:\n\n```python\nfoo_bar_bazz = config.FOO.BAR.BAZZ\n```\n\ninstead of this:\n\n```python\nfoo_bar_bazz = config["FOO"]["BAR"]["BAZZ"]\n```\n\n## ⚙️ Installation\n\nInstall Konfik via pip:\n\n```\npip install konfik\n```\n\n\n## 💡 Examples\n\nLet\'s see how you can parse a TOML config file and access the variables there. For demonstration, we\'ll be using the following `config.toml` file:\n\n```toml\n# example_config.toml\n\ntitle = "TOML Example"\n\n[owner]\nname = "Tom Preston-Werner"\ndob = 1979-05-27T07:32:00-08:00 # First class dates\n\n[servers]\n  [servers.alpha]\n  ip = "10.0.0.1"\n  dc = "eqdc10"\n\n  [servers.beta]\n  ip = "10.0.0.2"\n  dc = "eqdc10"\n\n[clients]\ndata = [ ["gamma", "delta"], [1, 2] ]\n```\n\nTo parse this in Python:\n\n```python\nfrom konfik import Konfik\n\n# Define the config path\nCONFIG_PATH_TOML = "config.toml"\n\n# Initialize the konfik class\nkonfik = Konfik(config_path=CONFIG_PATH_TOML)\n\n# Serialize and print the confile file\nkonfik.serialize()\n\n# Get the configuration dictionary from the konfik class\nconfig_toml = konfik.config\n\n# Access and print the variables\ntitle = config_toml.title\nowner = config_toml.owner\ndob = config_toml.owner.dob\ndatabase = config_toml.database.ports\nserver_ip = config_toml.servers.alpha.ip\nclients = config_toml.clients\n```\n\nThe `.serialize()` method will print your entire config file as a colorized Python dictionary object like this:\n\n```python\n{\n    \'title\': \'TOML Example\',\n    \'owner\': {\n        \'name\': \'Tom Preston-Werner\',\n        \'dob\': datetime.datetime(1979, 5, 27, 7, 32, tzinfo=<toml.tz.TomlTz object at\n0x7f2dfca308b0>)\n    },\n    \'database\': {\n        \'server\': \'192.168.1.1\',\n        \'ports\': [8001, 8001, 8002],\n        \'connection_max\': 5000,\n        \'enabled\': True\n    },\n    \'servers\': {\n        \'alpha\': {\'ip\': \'10.0.0.1\', \'dc\': \'eqdc10\'},\n        \'beta\': {\'ip\': \'10.0.0.2\', \'dc\': \'eqdc10\'}\n    },\n    \'clients\': {\'data\': [[\'gamma\', \'delta\'], [1, 2]]}\n}\n```\n\nKonfik also exposes a few command-line options for you to introspect your config file and variables. Run:\n\n```\nkonfik --help\n```\n\nThis will reveal the options associated with the CLI tool:\n\n```\nusage: konfik [-h] [--show SHOW] [--path PATH] [--serialize] [--version]\n\nKonfik CLI\n\noptional arguments:\n  -h, --help   show this help message and exit\n  --show SHOW  show variables from config file\n  --path PATH  add custom config file path\n  --serialize  print the serialized config file\n  --version    print konfik-cli version number\n```\n\nTo inspect the value of a specific variable in a `config.toml` file you can run:\n\n```\nkonfik --show servers.alpha.ip\n```\n\nIf you\'re using a config that\'s not named as `config.toml` then you can deliver the path using the `--path` argument like this:\n\n```\nkonfik --path settings/example_config.env --show name\n```\n\n## 🙋 Why\n\nWhile working with machine learning models, I wanted an easier way to tune the model parameters without mutating the Python files. I needed something that would simply enable me to access tuple or dictionary data structures from a config file. I couldn\'t find anything that doesn\'t try to do a gazillion of other kinds of stuff or doesn\'t come with the overhead of a significant learning curve.\n\nNeither DOTENV nor YAML catered to my need as I was after something that gives me the ability to store complex data structures without a lot of fuss -- so TOML it is. However,Konfik also supports DOTENV and JSON. Also, not having to write angle brackets ([""]) to access dictionary values is nice!\n\n## 🎉 Contribution Guidelines\n\nCurrently, Konfik doesn\'t support `.yaml` out of the box. Maybe that\'s something you\'d like to take a jab at. To do so,\n\n* Clone the repo\n* Spin up and activate your virtual environment. You can use anything between Python 3.6 to Python 3.9.\n* Install [poetry](https://python-poetry.org/docs/#installation)\n* Install the dependencies via:\n    ```\n    poetry install\n    ```\n* Make your changes to the `konfik/main.py` file\n\n* Run the tests via the following command. Make sure you\'ve Python 3.6 - Python 3.9 installed, otherwise tox would throw an error.\n    ```\n    tox\n    ```\n* Write a simple unit test for your change\n* Run the linter via:\n    ```\n    make linter\n    ```\n',
    'author': 'rednafi',
    'author_email': 'redowan.nafi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rednafi/konfik',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
