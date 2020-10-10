# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cyberbrain', 'cyberbrain.generated', 'cyberbrain.internal']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=19.3.0,<20.0.0',
 'cheap_repr>=0.4.2,<0.5.0',
 'crayons>=0.3.0,<0.4.0',
 'get-port>=0.0.5,<0.0.6',
 'grpcio>=1.30.0,<2.0.0',
 'jsonpickle>=1.4.1,<2.0.0',
 'more-itertools>=8.5.0,<9.0.0',
 'protobuf>=3.12.2,<4.0.0',
 'pygments>=2.6.1,<3.0.0',
 'shortuuid>=1.0.1,<2.0.0',
 'typing-extensions>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'cyberbrain',
    'version': '0.0.7',
    'description': 'Python debugging, redefined.',
    'long_description': '# Cyberbrain: Python debugging, **redefined**.\n\n[![support-version](https://img.shields.io/pypi/pyversions/cyberbrain)](https://img.shields.io/pypi/pyversions/cyberbrain)\n[![PyPI implementation](https://img.shields.io/pypi/implementation/cyberbrain.svg)](https://pypi.org/project/cyberbrain/)\n[![PyPI version shields.io](https://img.shields.io/pypi/v/cyberbrain.svg)](https://pypi.org/project/cyberbrain/)\n\nCyberbrain is a Python debugging solution aiming to **free programmers**. It visualizes **program execution** and **how each variable changes**.\n\nNever spend hours stepping through a program, let Cyberbrain tell you.\n\n![](https://user-images.githubusercontent.com/2592205/95418789-1820b480-08ed-11eb-9b3e-61c8cdbf187a.png)\n\n## Install\n\nCyberbrain consists of a Python library and various editor/IDE integrations. Currently VS Code is the only supported editor, but we have **[plans](https://github.com/laike9m/Cyberbrain/issues/24)** to expand the support.\n\nTo install Cyberbrain:\n\n```\npip install cyberbrain\ncode --install-extension laike9m.cyberbrain\n```\n\nOr if you prefer, install from [PyPI](https://pypi.org/project/cyberbrain/) and [VS Code marketplace](https://marketplace.visualstudio.com/items?itemName=laike9m.cyberbrain).\n\n**Or, you can try Cyberbrain directly from your browser:** [![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#snapshot/a473ffc1-a764-4062-953c-5a95e13404c1)\n\n## How to Use\n\nSuppose you want to trace a function called `foo`, just decorate it with `@trace`:\n\n```python\nfrom cyberbrain import trace\n\n@trace  # You can disable tracing with `@trace(disabled=True)`\ndef foo():\n    ...\n```\n\nCyberbrain keeps your workflow unchanged. You run a program (from vscode or command line, both work), call **"Initialize Cyberbrain"** from the [command palette](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette), and a new panel will be opened to visualize how your program execution.\n\nThe following gif demonstrates the workflow (click to view the full size image):\n\n![usage](https://user-images.githubusercontent.com/2592205/95430485-ac484700-0900-11eb-814f-41ca84c022f9.gif)\n\nFeatures provided:\n- Dataflow analysis\n- Variable tracing (try hover on any variable, it only highlights **relevant** variables)\n- Object inspection (value is logged in the opened devtools console)\n- Expect more to come 🤟\n\nRead our [documentation](docs/Features.md) to learn more about Cyberbrain\'s features.\n\nNote: Cyberbrain may conflict with other debuggers. If you set breakpoints and use VSC\'s debugger, Cyberbrain may not function normally. Generally speaking, **prefer "Run Without Debugging"** (like shown in the gif).\n\n## Status Quo and Milestones\n\n*Updated 2020.9*\n\nCyberbrain is new and under active development, bugs are expected. If you met any, I appreciate if you can [create an issue](https://github.com/laike9m/Cyberbrain/issues/new). At this point, you should **NOT** use Cyberbrain in production.\n\nMilestones for the project are listed below, which may change over time. Generally speaking, we\'ll release 1.0 when it reaches  "*Production ready*".\n\n| Milestone        | Description                                                           | Status |\n|------------------|-----------------------------------------------------------------------|--------|\n| Examples ready   | Cyberbrain works on examples (in the `examples/` folder)      | WIP    |\n| Live demo ready  | Cyberbrain can work with code you write in a live demo, in most cases | Not started    |\n| Scripts ready     | Cyberbrain can work with most "scripting" programs                      | Not started    |\n| Announcement ready | Cyberbrain is ready to be shared on Hacker News and Reddit. **Please don\'t broadcast Cyberbrain before it reaches this milestone.**                  | Not started    |\n| Production ready | Cyberbrain can work with most programs in production                  | Not started    |\n\nNote that v1.0 means Cyberbrain is stable in the features it supports, it does **NOT** mean Cyberbrain is feature complete. Major features planned for each future version are listed below. Again, expect it to change at any time.\n\n| Version | Features                        |\n|:-------:|---------------------------------|\n| 1.0     | Code & trace interaction ([#7][m1]), remote debugging, trace dump\n| 2.0     | Multi-frame tracing             |\n| 3.0     | Fine-grained symbol tracing     |\n| 4.0     | Async & multi-threading support |\n\n[m1]: https://github.com/laike9m/Cyberbrain/issues/7\n\nVisit the project\'s [kanban](https://github.com/laike9m/Cyberbrain/projects/1) to learn more about the current development schedule.\n\n## How does it compare to PySnooper?\n\nCyberbrain and PySnooper share the same goal of reducing programmers\' work while debugging. However they are fundamentally different: Cyberbrain traces and shows the sources of each variable change, while PySnooper only logs them. The differences should be pretty obvious after you tried both.\n\n## Community\n\nJoin the [Cyberbrain community Discord](https://discord.gg/2TFYtBh) 💬 and follow us on Twitter [@PyCyberbrain](https://twitter.com/PyCyberbrain) 🐦.\n\nAll questions & suggestions & discussions welcomed.\n\n## Interested in Contributing?\nGet started [here](https://github.com/laike9m/Cyberbrain/blob/master/docs/Development.md).\n\n## Support\n\nCyberbrain is a **long-term** project, your support is critical to sustain it. Let\'s make it the best Python debugging tool 🤟!\n\n[![](https://www.buymeacoffee.com/assets/img/guidelines/download-assets-1.svg)](https://www.buymeacoffee.com/cyberbrain)\n',
    'author': 'laike9m',
    'author_email': 'laike9m@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/laike9m/Cyberbrain',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<3.9.0',
}


setup(**setup_kwargs)
