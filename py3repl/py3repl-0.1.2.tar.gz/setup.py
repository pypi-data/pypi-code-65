# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py3repl']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.3,<0.5.0']

entry_points = \
{'console_scripts': ['pyrepl = py3repl.pyrepl:repl']}

setup_kwargs = {
    'name': 'py3repl',
    'version': '0.1.2',
    'description': 'A cli to mimic python REPL implementation',
    'long_description': "## py3repl\nA tool to mimic the python REPL\n\n### Installation\n```bash\npip install py3repl\n```\n\n### Usage\n- Linux\n\n    ```bash\n    # call pyrepl from command-line\n\n    pyrepl\n    ```\n\n- Windows\n\n    ```bash\n    # call pyrepl from command line\n    pyrepl\n\n    # if this failes, try\n    python -m py3repl.pyrepl # this should work\n    ```\n\n### Demo\n\n![final demo](files/final_demo.gif)\n\n\n### I haven't tested a lot. So chances of bugs are very high. Please do report or make a pull request. All contributions are welcome.",
    'author': 'Amal Shaji',
    'author_email': 'amalshajid@gmail.com',
    'maintainer': 'Amal Shaji',
    'maintainer_email': 'amalshajid@gmail.com',
    'url': 'https://github.com/amalshaji/pyrepl/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
