# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_insta']

package_data = \
{'': ['*']}

install_requires = \
['pytest>=6.0.2,<7.0.0', 'wrapt>=1.12.1,<2.0.0']

entry_points = \
{'pytest11': ['insta = pytest_insta.plugin']}

setup_kwargs = {
    'name': 'pytest-insta',
    'version': '0.0.1',
    'description': 'A flexible and user-friendly snapshot testing plugin for pytest',
    'long_description': '# pytest-insta\n\n> A flexible and user-friendly snapshot testing plugin for pytest.\n\n```python\nassert snapshot() == "awesome!"\n```\n\n## Introduction\n\nSnapshot testing makes it easy to monitor and approve changes by comparing the result of an operation against a previous reference value.\n\nThis project borrows from a lot of other implementations but reinterprets what it means to work with snapshots in an expressive language like Python. It also tries to feel as native to [`pytest`](https://docs.pytest.org/en/stable/) as possible with its integrated reviewing tool.\n\n### Features\n\n- Expressive and familiar assertion syntax\n- Named and unnamed snapshots\n- Handles text, binary, hexdump, json and pickle snapshots out-of-the-box\n- The plugin can be extended with custom snapshot formats\n- Integrated reviewing tool with live repl for inspecting the new value and the old value\n\n### Credits\n\n- [`insta`](https://github.com/mitsuhiko/insta) (rust)\n\n  Armin\'s work was the initial inspiration for this project and shaped the reviewing workflow. The name was cool too. 😎\n\n- [`jest`](https://jestjs.io/docs/en/snapshot-testing) (javascript)\n\n  Jest enabled the mass-adoption of snapshot testing throughout the JavaScript ecosystem and now basically stands as the reference when it comes to what snapshot testing is supposed to look like.\n\n## Installation\n\nThe package can be installed with `pip`.\n\n```bash\n$ pip install pytest-insta\n```\n\n## Contributing\n\nContributions are welcome. This project uses [`poetry`](https://python-poetry.org).\n\n```bash\n$ poetry install\n```\n\nYou can run the tests with `poetry run pytest`.\n\n```bash\n$ poetry run pytest\n```\n\nThe project must type-check with [`mypy`](http://mypy-lang.org) and [`pylint`](https://www.pylint.org) shouldn\'t report any error.\n\n```bash\n$ poetry run mypy\n$ poetry run pylint pytest_insta tests\n```\n\nThe code follows the [`black`](https://github.com/psf/black) code style. Import statements are sorted with [`isort`](https://pycqa.github.io/isort/).\n\n```bash\n$ poetry run isort pytest_insta tests\n$ poetry run black pytest_insta tests\n$ poetry run black --check pytest_insta tests\n```\n\n---\n\nLicense - [MIT](https://github.com/vberlier/pytest-insta/blob/master/LICENSE)\n',
    'author': 'Valentin Berlier',
    'author_email': 'berlier.v@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vberlier/pytest-insta',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
