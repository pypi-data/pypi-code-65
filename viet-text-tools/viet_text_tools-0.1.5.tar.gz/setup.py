# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['viet_text_tools', 'viet_text_tools.tests']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'viet-text-tools',
    'version': '0.1.5',
    'description': 'Functions for working with Vietnamese text',
    'long_description': "Viet Text Tools\n===============\n\nFunctions for working with Vietnamese text\n\nInstallation\n------------\n\nTo get the latest stable release from PyPi\n\n.. code-block:: bash\n\n    pip install viet_text_tools\n\nUsage\n-----\n\nnormalize_diacritics()\n~~~~~~~~~~~~~~~~~~~~~~\n\nYou can normalize diacritics for a Vietnamese word.  The return value is in composed (NFC) form\n\n.. code-block:: python\n\n    normalize_diacritics('nghìên') == 'nghiền'\n\nPass ``new_style=True`` to use new style tone placement\n\n.. code-block:: python\n\n    normalize_diacritics('thủy', new_style=True) == 'thuỷ'\n\nPass ``decomposed=True`` to return a string in decomposed (NFD) form\n\n.. code-block:: python\n\n    len(normalize_diacritics('thủy')) == 4\n    len(normalize_diacritics('thủy', decomposed=True)) == 5\n\nvietnamese_sort_key()\n~~~~~~~~~~~~~~~~~~~~~\n\nA key function for use with sorted() to sort Vietnamese text with the correct collation order\n\n.. code-block:: python\n\n    words = ['anh', 'ba', 'áo', 'cắt', 'cá', 'cả']\n    sorted(words) == ['anh', 'ba', 'cá', 'cả', 'cắt', 'áo']\n    sorted(words, key=vietnamese_sort_key) == ['anh', 'áo', 'ba', 'cả', 'cá', 'cắt']\n\nvietnamese_case_insensitive_sort_key()\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\nSame as `vietnamese_sort_key()` but case-insensitive.\n",
    'author': 'Enrico Barzetti',
    'author_email': 'enricobarzetti@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/enricobarzetti/viet_text_tools',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
