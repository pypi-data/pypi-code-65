# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rezipe']

package_data = \
{'': ['*']}

install_requires = \
['pint>=0.16.1,<0.17.0']

setup_kwargs = {
    'name': 'rezipe',
    'version': '0.1.1',
    'description': 'A way to write down your cooking/baking recipes in Python. This is an actual library, no joke (period). Made with ❤ for everyone with minimum coding literacy.',
    'long_description': '# Rezipe 👨\u200d🍳👩\u200d🍳🍽\nA way to write down your cooking/baking recipes in Python. This is an actual library, no joke (period). Made with ❤ for everyone with minimum coding literacy.\n\n> ⛑ This is under developement.\n\n```python\nimport pint\n\nfrom rezipe import Measure, recipe\nfrom rezipe.wares import Pot\nfrom rezipe.ingredients import RegularTofu, SnowPea, EnokiMushroom, DashiSoup, Miso\n\nureg  = pint.UnitRegistry()\n\nclass MisoSoup(Rezipe):\n    """\n    A simple miso soup by Rie\n    """\n    ref = "https://tasty.co/recipe/miso-soup"\n\n    # kichenwares\n    pot: Pot = Pot()\n\n    # Ingredients\n    dashi: DashiSoup = Measure(360 * ureg.mL)\n    tofu: RegularTofu = Measure(200 * ureg.gram)\n    pea: SnowPea = Measure(75 * ureg.gram)\n    mushroom: EnokiMushroom = Measure(55 * ureg.gram)\n    miso: Miso = Measure(2*ureg(\'tablespoon\'))\n\n    @recipe\n    async def make(self):\n        # class variable auto expose from method variable?\n        pot += dashi\n        await pot.boil()\n\n        # self assign inplace async, is it even possible?\n        await tofu.cut(style="cube")\n\n        # method chaining\n        await pea.trim().cut(in="half")\n\n        await mushroom.cut(remove="end")\n\n        pot += tofu + pea + mushroom\n        await pot.slimmer().for(3*ureg.min)\n\n        assert pot.heat.isOff\n        miso = await miso.dissolve(with=pot.soup)\n        pot.add(miso)\n\n        await pot.boil(progress=0.75)\n\n        self.serve(pot)\n```\n\n## Features\n* Accept concurrent async/await - real home cooker do multiple things at once\n* Auto Convertion - enable percise measurement by default\n* Easy to fork(searchable, copy and modify) - that is the nature of open source.\n* Crystal Clear - yep totally logical and very descriptive\n\n\n## Roadmap\n* Autogen printable recipe/VSCode plugins for assisting read/cli\n* Works with your smart home/IoT device\n* Auto order/pre-order from your nearby market/farmer\n* Auto global ingredient subsitution - how to find nashville hot sauce/butter milk in Udon Thani?\n* Auto Nutrition\n* Add documentaion/test\n* Library of localized ingredients - thanks to inheritance of class, not the all white rice is equal, Not all beef are equal,  `class HomMaliRice(WhiteRice):`, `class Wagyu(Beef)`\n* Make this for all popular programing languages\n* Able to create a opitimal cooking pipeline when do multiple recipes/dishes things at once\n* Able to create a opitimal cooking pipeline when do multiple recipes/dishes things at once\n* Enable [Bidirection Alias](https://dev.to/circleoncircles/rewrite-link-bidirectional-aliasing-in-python-ekl) for truly world citizen recipe i.e. `dough.bake` == `แป้งโด.อบ` == `面团.烤`\n\n## Style\nThis will be a modern python lib.',
    'author': 'Nutchanon Ninyawee',
    'author_email': 'nutchanon@codustry.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CircleOnCircles/recipe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
