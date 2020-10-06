# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nbjuniper']

package_data = \
{'': ['*']}

install_requires = \
['markdown>=3.2.2,<4.0.0', 'pyyaml>=5.3.1,<6.0.0']

entry_points = \
{'console_scripts': ['nbjuniper = nbjuniper.cli:main']}

setup_kwargs = {
    'name': 'nbjuniper',
    'version': '0.3.1',
    'description': 'Convert Jupyter Notebooks into runnable HTML files with Juniper (https://github.com/ines/juniper).',
    'long_description': '# nbjuniper\nConvert Jupyter Notebooks and Jupyter-book documentation into executable code with [Juniper](https://github.com/ines/juniper) + [Binder](https://mybinder.org)\n\n<p align="center">\n<img src="screenshot.gif"/>\n</p>\n\n---\n\n## Installation\n**conda**\n```sh\nconda install -c conda-forge nbjuniper\n```\n\n**pip**\n```sh\npip install nbjuniper\n```\n\n## Standalone (ipynb -> html) usage\n```sh\nnbjuniper example_notebook.ipynb\n```\n\nThe above command will create (or clobber if it exists!) the file example_notebook.html,\nwhich can be opened as a standalone webpage or embedded in another page. \n\n## Jupyter-book (html -> html) usage\n\nTo activate Junper for all code cells in documentation that has already been built with\n`jupyter-book build`, use the jupyter-book mode (it is automatically recursive):\n\n```sh\nnbjuniper -j documentation_folder\n```\n\nThis command adds an nbjuniper header to each HTML file in your documentation_folder. It will (should)\nonly change the appearance and behavior of code cells.\n\n## Under the hood\n\n`nbjuniper` creates _Juniper_ notebooks- they are *not* quite the same as _Ipython/Jupyter_ notebooks ([what\'s the difference?](#what-nbjuniper-cannot-do)) The html\nfile(s) created by `nbjuniper` automatically link your code to a [MyBinder](https://mybinder.org) instance that\nserves as the backend for executing the code.\n\n## Defaults and how to override them\n\n### MyBinder repository\nBy default, `nbjuniper` connects your code to my extremely minimal python Binder ([ashtonmv/python_binder](https://github.com/ashtonmv/python_binder)), where only python and its native libraries are installed. If your code has any dependencies, you\'ll\nwant to connect it to your own MyBinder docker image. If you haven\'t done so, create the MyBinder image for your repo [here](https://mybinder.org) and then run\n\n```sh\nnbjuniper example_notebook.ipynb --repo github_username/binder_repo\n```\n\nWhere you\'ve replaced `github_username` with your github username and `binder_repo` with the name of the repository for which you\'ve created the MyBinder docker image.\n\n### Using other BinderHubs\nIf you have your own BinderHub or are hosting your notebook on someone else\'s hub (e.g. [GESIS](https://notebooks.gesis.org)),\nyou\'ll want to override MyBinder.org as the default server:\n\n```sh\nnbjuniper example_notebook.ipynb --binderhub https://notebooks.gesis.org --repo github_username/binder_repo\n```\n\n### Styling\nThe default style used to create Juniper notebooks is [monokai](https://monokai.pro/). The theme controls the syntax\nhighlighting in each cell as well as the cells\' general appearance.\n\nThe easiest way to switch themes is using a bundled theme (one of those listed under cdn/styles):\n\n```sh\nnbjuniper example_notebook.ipynb --theme material\n```\n\nYou can also create your own style and hardcode it in\n(see [Removing the html head](#removing-the-html-head)). Adding new themes is very easy; see the examples under cdn/styles.\nI am slowly adding more themes that are already available for CodeMirror; if you want to help me or to add your own theme\nto the nbjuniper CDN please just submit a PR!\n\n### Full control of Juniper settings\nFor those who are familiar with [Juniper](https://github.com/ines/juniper), (and if you\'re not check it out! It\'s awesome)\nyou can customize every option used to create the Juniper client like so:\n\n```sh\nnbjuniper example_notebook.ipynb -f example_config.yaml\n```\n\nwhere example_config.yaml should have the same form as the example provided in this repository:\n\n```yaml\nurl: https://binder.michael-ashton.com  # must be a binderhub with CORS enabled\nrepo: ashtonmv/conda  # your binder repo\nisolateCells: true  # Cells don\'t pass variables to one another\nuseStorage: false  # Don\'t cache the binder (will be slow)\nmsgLoading: "Loading..."  # msg to display while loading (doesn\'t go away if no stdout!)\n...etc\n```\n\nSee the [Juniper documentation](https://github.com/ines/juniper) for a full list of settings; everthing in this file will be passed\nto the Juniper instance.\n\n### Removing the html head\nIf you\'re going to embed multiple Juniper notebooks into a single page, you don\'t want to include the html head in\neach one. That would import the stylesheet and javascript resources once per notebook, which can slow down your page load\ntime and is just sloppy. To chop off the head from a Juniper notebook, use the admittedly gruesome command\n\n```sh\nnbjuniper example_notebook.ipynb --decapitate\n```\n\nThis will create two files: the typical example_notebook.html and the severed juniper_head.html. From here you\ncan either discard juniper_head.html and write your own html head, or you can embed juniper_head.html at the top\nof your page where you\'re including the notebooks so that it\'s only read in once for the whole page. To prevent writing\nthe juniper_head.html file at all, replace `--decapitate` with `--no-head`.\n\n### What nbjuniper cannot do\nAnything that requires instantaneous feedback between the page and the MyBinder server, including certain widgets\nand tab autocompletion, won\'t work. nbjuniper also intentionally doesn\'t give you a full jupyter "header"- if you\nwant the page to look just like a jupyter notebook, there\'s a good chance you should just be redirecting to\nMyBinder itself.\n',
    'author': 'Michael Ashton',
    'author_email': 'ashtonmv@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ashtonmv/nbjuniper',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
