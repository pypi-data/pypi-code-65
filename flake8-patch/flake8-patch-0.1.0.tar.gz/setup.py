# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flake8_patch', 'flake8_patch.visitors']

package_data = \
{'': ['*']}

install_requires = \
['flake8_plugin_utils>=1.3.1,<2.0.0']

entry_points = \
{'flake8.extension': ['MOC0 = flake8_patch.plugin:PatchPlugin']}

setup_kwargs = {
    'name': 'flake8-patch',
    'version': '0.1.0',
    'description': 'A flake8 plugin checking for mocking issues.',
    'long_description': '# flake8-patch\n\nA `flake8` plugin checking for mocking issues.\n\nCurrently reports the code `PAT001` when assignments to imported objects are detected.\n\n## Bad code example\n\n```python\nfrom some_module import SomeClass\n\ndef test_something():\n    SomeClass.some_method = lambda: 42\n```\n\nThis is bad because `SomeClass.some_method` might be used directly or indirectly in another test, which will break randomly depending on the execution order.\n\n## Good code example\n\n```python\nfrom some_module import SomeClass\n\ndef test_something(mocker):\n    mocker.patch.object(SomeClass, "some_method", return_value=42)\n```\n\nThis uses the mocker fixture from `pytest-mock` to automatically unwind the patch after the test method runs.\n\n## Change Log\n\n**Unreleased**\n\n...\n\n**0.1.0 - 2020-10-02**\n\nAdd PAT001: assignment to imported name\n',
    'author': 'Luiz Geron',
    'author_email': 'luiz@geron.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/flake8-patch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
