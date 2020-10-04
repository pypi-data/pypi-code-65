# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rezipe']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'rezipe',
    'version': '0.1.0',
    'description': 'A way to write down your cooking/baking recipes in Python. This is an actual library, no joke (period). Made with ❤ for everyone with minimum coding literacy.',
    'long_description': '# Recipe 👨\u200d🍳👩\u200d🍳🍽\nA way to write down your cooking/baking recipes in Python. This is an actual library, no joke (period). Made with ❤ for everyone with minimum coding literacy.\n\n## Features\n* Accept concurrent async/await - real home cooker do multiple things at once\n* Auto Convertion - enable percise measurement by default\n* Easy to fork(searchable, copy and modify) - that is the nature of open source.\n* Crystal Clear - yep totally logical and very descriptive\n\n\n## Roadmap\n* Autogen printable recipe/VSCode plugins for assisting read/cli\n* Works with your smart home/IoT device\n* Auto order/pre-order from your nearby market/farmer\n* Auto global ingredient subsitution - how to find nashville hot sauce/butter milk in Udon Thani?\n* Auto Nutrition\n* Add documentaion/test\n* Library of localized ingredients - thanks to inheritance of class, not the all white rice is equal, Not all beef are equal,  `class HomMaliRice(WhiteRice):`, `class Wagyu(Beef)`\n* Make this for all popular programing languages\n*\n* Enable [Bidirection Alias](https://dev.to/circleoncircles/rewrite-link-bidirectional-aliasing-in-python-ekl) for truly world citizen recipe i.e. `dough.bake` == `แป้งโด.อบ` == `面团.烤`\n\n## Style\nThis will be a modern python lib.',
    'author': 'Nutchanon Ninyawee',
    'author_email': 'nutchanon@codustry.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CircleOnCircles/recipe',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
