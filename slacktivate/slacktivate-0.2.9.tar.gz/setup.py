# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['slacktivate',
 'slacktivate.cli',
 'slacktivate.helpers',
 'slacktivate.input',
 'slacktivate.macros',
 'slacktivate.slack']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=7.2.0,<8.0.0',
 'backoff>=1.10.0,<2.0.0',
 'click-option-group>=0.5.1,<0.6.0',
 'click>=7.1.2,<8.0.0',
 'click_help_colors>=0.8,<0.9',
 'click_spinner>=0.1.10,<0.2.0',
 'comma>=0.5.3,<0.6.0',
 'jinja2>=2.11.2,<3.0.0',
 'python-dotenv>=0.14.0,<0.15.0',
 'pyyaml>=5.3.1,<6.0.0',
 'requests>=2.24.0,<3.0.0',
 'slack-scim>=1.1.0,<2.0.0',
 'slackclient>=2.8.0,<3.0.0',
 'tqdm>=4.49.0,<5.0.0',
 'yaql>=1.1.3,<2.0.0']

entry_points = \
{'console_scripts': ['slacktivate = slacktivate.cli.__main__:main']}

setup_kwargs = {
    'name': 'slacktivate',
    'version': '0.2.9',
    'description': 'Slacktivate is a Python library and Command-Line Interface to assist in the provisioning of a Slack workspace.',
    'long_description': '# Slacktivate\n\nSlacktivate is a Python library and Command-Line Interface\nto assist in the provisioning of a Slack workspace, using\nboth the Slack API and the Slack SCIM API.\n\n## Prerequisites: Having Owner Access and Getting an API Token\n\nIn order to use the SCIM API, you need to be an owner of the workspace, and obtain an API token with `admin` scope.\n\nAs explained in [the official Slack SCIM API documentation](https://api.slack.com/scim#access), the easiest way to obtain a valid token for the purposes of SCIM provisioning is as follows:\n1. As *a Workspace/Organization Owner*, create [a new app for your workspace](https://api.slack.com/apps?new_app=1) (see [here](https://api.slack.com/start/overview#creating) for the documentation).\n2. Add the `admin` OAuth scope to [the "User Token Scopes" section](https://api.slack.com/authentication/quickstart#configuring).\n3. Install the app to your workspace (see [here](https://api.slack.com/start/overview#installing_distributing) for the documentation).\n4. Use the generated token (if you are provided with multiple tokens, use the "OAuth Access Token" not the "Bot User OAuth Access Token").\n\nNote that you can easily *reinstall your app* with different permissions if it turns out you did not select all the necessary permissions.\n\n\n## License\n\nThis project is licensed [under the LGPLv3 license](https://www.gnu.org/licenses/lgpl-3.0.en.html),\nwith the understanding that importing a Python modular is similar in spirit to dynamically linking\nagainst it.\n\n- You can use the library/CLI `slacktivate` in any project, for any purpose,\n  as long as you provide some acknowledgement to this original project for\n  use of the library (for open source software, just explicitly including\n  `slacktivate` in the dependency such as a `pyproject.toml` or `Pipfile`\n  is acknowledgement enough for me!).\n\n- If you make improvements to `slacktivate`, you are required to make those\n  changes publicly available.\n\nThis license is compatible with the license of all the dependencies as\ndocumented in [this project\'s own `pyproject.toml`](https://github.com/jlumbroso/slacktivate/blob/master/pyproject.toml#L29-L49).\n',
    'author': 'Jérémie Lumbroso',
    'author_email': 'lumbroso@cs.princeton.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jlumbroso/slacktivate',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
