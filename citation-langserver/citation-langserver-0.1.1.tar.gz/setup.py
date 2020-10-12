# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['citation_langserver']

package_data = \
{'': ['*']}

install_requires = \
['bibparse>=1.0.0,<2.0.0', 'pygls>=0.9.0,<0.10.0']

entry_points = \
{'console_scripts': ['citation-langserver = citation_langserver.cli:cli']}

setup_kwargs = {
    'name': 'citation-langserver',
    'version': '0.1.1',
    'description': 'A language server for managing citations stored in BibTeX and BibLaTeX files.',
    'long_description': '# citation-langserver\n\ncitation-langserver is a language server for working with citations stored in BibTeX or BibLaTeX files.\n\ncitation-langserver supports code completion, hover, jump to definition, and find references. It supports absolute file paths for bibliographies, relative file paths, as well as glob-based file paths. It is compatible with all clients that support the [Language Server Protocol](https://langserver.org/)\n\n# Installation\n\nRun `pip3 citation-langserver` to install.\n\n# Usage\n\nConfigure `citation-langserver` as you would any other LSP in your text editor of choice.\n\nFor instance, using [CoC](https://github.com/neoclide/coc.nvim) in Vim, you might add the following to your `coc-settings.json` file:\n\n```json\n  "languageserver": {\n    "citation": {\n      "command": "/usr/local/bin/citation-langserver",\n      "filetypes": ["markdown"],\n      "settings": {\n        "citation": {\n          "bibliographies": [\n            "~/library.bib",\n\t\t\t"./*.bib"\n          ]\n        }\n      }\n    }\n  }\n```\n\n## Configuration\n\nThe setting `citation.bibliographies` needs to be sent by the client to the server and contain an array of file paths. The file paths can include:\n\n- Absolute paths\n- Relative paths\n- Globs (absolute or relative)\n',
    'author': 'oncomouse',
    'author_email': 'oncomouse@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/oncomouse/citation-langserver',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
