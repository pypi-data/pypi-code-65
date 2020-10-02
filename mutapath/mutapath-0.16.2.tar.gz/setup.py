# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mutapath']

package_data = \
{'': ['*']}

install_requires = \
['cached-property==1.5.2',
 'filelock==3.0.12',
 'path>=13.1,<16.0',
 'singletons==0.2.5']

setup_kwargs = {
    'name': 'mutapath',
    'version': '0.16.2',
    'description': 'mutable pathlib',
    'long_description': '# mutapath\n\n[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/matfax/mutapath/build/master?style=for-the-badge)](https://github.com/matfax/mutapath/actions)\n[![Codecov](https://img.shields.io/codecov/c/github/matfax/mutapath?style=for-the-badge)](https://codecov.io/gh/matfax/mutapath)\n[![Documentation Status](https://readthedocs.org/projects/mutapath/badge/?version=latest&style=for-the-badge)](https://mutapath.readthedocs.io/en/latest/?badge=latest)\n[![Dependabot Status](https://img.shields.io/badge/dependabot-enabled-blue?style=for-the-badge&logo=dependabot&color=0366d6)](https://github.com/matfax/mutapath/network/updates)\n[![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/mutapath?style=for-the-badge)](https://libraries.io/pypi/mutapath)\n[![CodeFactor](https://www.codefactor.io/repository/github/matfax/mutapath/badge?style=for-the-badge)](https://www.codefactor.io/repository/github/matfax/mutapath)\n[![security: bandit](https://img.shields.io/badge/security-bandit-purple.svg?style=for-the-badge)](https://github.com/PyCQA/bandit)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mutapath?style=for-the-badge)](https://pypi.org/project/mutapath/)\n[![PyPI](https://img.shields.io/pypi/v/mutapath?color=%2339A7A6&style=for-the-badge)](https://pypi.org/project/mutapath/)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/mutapath?color=ff69b4&style=for-the-badge)](https://pypistats.org/packages/mutapath)\n[![GitHub License](https://img.shields.io/github/license/matfax/mutapath.svg?style=for-the-badge)](https://github.com/matfax/mutapath/blob/master/LICENSE)\n[![GitHub last commit](https://img.shields.io/github/last-commit/matfax/mutapath?color=9cf&style=for-the-badge)](https://github.com/matfax/mutapath/commits/master)\n\n\nThis library is for you if you are also annoyed that there is no mutable pathlib wrapper for use cases in which paths are often changed.\nmutapath solves this by wrapping both, the Python 3 pathlib library, and the alternate  [path library](https://pypi.org/project/path/), and providing a mutable context manager for them.\n\n## MutaPath Class\n\nThe MutaPath Class allows direct mutation of its attributes at any time, just as any mutable object.\nOnce a file operation is called that is intended to modify its path, the underlying path is also mutated.\n\n```python\n>>> from mutapath import MutaPath\n```\n```python\n>>> folder = MutaPath("/home/joe/doe/folder/sub")\n>>> folder\nPath(\'/home/joe/doe/folder/sub\')\n```\n```python\n>>> folder.name = "top"\n>>> folder\nPath(\'/home/joe/doe/folder/top\')\n```\n```python\n>>> next = MutaPath("/home/joe/doe/folder/next")\n>>> next\nPath(\'/home/joe/doe/folder/next\')\n```\n```python\n>>> next.rename(folder)\n>>> next\nPath(\'/home/joe/doe/folder/top\')\n>>> next.exists()\nTrue\n>>> Path(\'/home/joe/doe/folder/sub\').exists()\nFalse\n```\n\n## Path Class\n\nThis class is immutable by default, just as the `pathlib.Path`. However, it allows to open a editing context via `mutate()`.\nMoreover, there are additional contexts for file operations. They update the file and its path while closing the context.\nIf the file operations don\'t succeed, they throw an exception and fall back to the original path value.\n\n```python\n>>> from mutapath import Path\n```\n```python\n>>> folder = Path("/home/joe/doe/folder/sub")\n>>> folder\nPath(\'/home/joe/doe/folder/sub\')\n```\n```python\n>>> folder.name = "top"\nAttributeError: mutapath.Path is an immutable class, unless mutate() context is used.\n>>> folder\nPath(\'/home/joe/doe/folder/sub\')\n```\n```python\n>>> with folder.mutate() as m:\n...     m.name = "top"\n>>> folder\nPath(\'/home/joe/doe/folder/top\')\n```\n```python\n>>> next = Path("/home/joe/doe/folder/next")\n>>> next.copy(folder)\n>>> next\nPath(\'/home/joe/doe/folder/next\')\n>>> folder.exists()\nTrue\n>>> folder.remove()\n```\n```python\n>>> with next.renaming() as m:\n...     m.stem = folder.stem\n...     m.suffix = ".txt"\n>>> next\nPath("/home/joe/doe/folder/sub.txt")\n>>> next.exists()\nTrue\n>>> next.with_name("next").exists()\nFalse\n```\n\nFor more in-depth examples, check the tests folder.\n\n## Locks\n\nSoft Locks can easily be accessed via the lazy lock property.\nMoreover, the mutable context managers in `Path` (i.e., `renaming`, `moving`, `copying`) allow implicit locking.\nThe lock object is cached as long as the file is not mutated. \nOnce the lock is mutated, it is released and regenerated, respecting the new file name.\n\n```python\n>>> my_path = Path(\'/home/doe/folder/sub\')\n>>> with my_path.lock:\n...     my_path.write_text("I can write")\n```\n\n## Hashing\n\nmutapath paths are hashable by caching the generated hash the first time it is accessed.\nHowever, it also adds a warning so that unintended hash usage is avoided.\nOnce mutated after that, the generated hashes don\'t provide collision detection in binary trees anymore.\nDon\'t use them in sets or as keys in dicts.\nUse the explicit string representation instead, to make the hashing input transparent.\n\n```python\n>>> p = Path("/home")\n>>> hash(p)\n1083235232\n>>> hash(Path("/home")) == hash(p)\nTrue\n>>> with p.mutate() as m:\n...     m.name = "home4"\n>>> hash(p) # same hash\n1083235232\n>>> hash(Path("/home")) == hash(p) # they are not equal anymore\nTrue\n```\n',
    'author': 'matfax',
    'author_email': 'matthias.fax@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/matfax/mutapath',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
