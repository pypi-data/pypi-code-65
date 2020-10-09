# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyrcrack']

package_data = \
{'': ['*']}

install_requires = \
['async-timeout>=3.0,<4.0',
 'docopt>=0.6.2,<0.7.0',
 'dotmap>=1.3.17,<2.0.0',
 'geopy>=2.0.0,<3.0.0',
 'mac-vendor-lookup>=0.1.11,<0.2.0',
 'parse>=1.12,<2.0',
 'pyshark>=0.4.2,<0.5.0',
 'pytest-asyncio>=0.14.0,<0.15.0',
 'rich>=7.1.0,<8.0.0',
 'stringcase>=1.2,<2.0',
 'xmltodict>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'pyrcrack',
    'version': '1.1.0',
    'description': 'Pythonic aircrack-ng bindings',
    'long_description': '.. image:: ./docs/pythonlovesaircrack.png\n\n**Python aircrack-ng bindings**\n\nPyrCrack is a Python API exposing a common aircrack-ng API. As AircrackNg will\nrun in background processes, and produce parseable output both in files and\nstdout, the most pythonical approach are context managers, cleaning up after \n\n|pypi| |release| |downloads| |python_versions| |pypi_versions| |coverage| |actions|\n\n.. |pypi| image:: https://img.shields.io/pypi/l/pyrcrack\n.. |release| image:: https://img.shields.io/librariesio/release/pypi/pyrcrack\n.. |downloads| image:: https://img.shields.io/pypi/dm/pyrcrack\n.. |python_versions| image:: https://img.shields.io/pypi/pyversions/pyrcrack\n.. |pypi_versions| image:: https://img.shields.io/pypi/v/pyrcrack\n.. |coverage| image:: https://codecov.io/gh/XayOn/pyrcrack/branch/develop/graph/badge.svg\n    :target: https://codecov.io/gh/XayOn/pyrcrack\n.. |actions| image:: https://github.com/XayOn/pyrcrack/workflows/CI%20commit/badge.svg\n    :target: https://github.com/XayOn/pyrcrack/actions\n\nInstallation\n------------\n\nThis library is available on `Pypi <https://pypi.org/project/pyrcrack/>`_, you can install it directly with pip::\n\n        pip install pyrcrack\n\nUsage\n-----\n\nThis library exports a basic aircrack-ng API aiming to keep always a small\nreadable codebase.\n\nThis has led to a simple library that executes each of the aircrack-ng\'s suite commands\nand auto-detects its usage instructions. Based on that, it dinamically builds\nclasses inheriting that usage as docstring and a run() method that accepts\nkeyword parameters and arguments, and checks them BEFORE trying to run them.\n\nSome classes expose themselves as async iterators, as airodump-ng\'s wich\nreturns access points with its associated clients.\n\nYou can have a look at the examples/ folder for some usage examples, such as\nthe basic "scan for targets", that will list available interfaces, let you\nchoose one, put it in monitor mode, and scan for targets updating results each\n2 seconds.\n\n.. code:: python\n\n        import asyncio\n\n        import pyrcrack\n\n        from rich.console import Console\n        from rich.prompt import Prompt\n\n\n        async def scan_for_targets():\n            """Scan for targets, return json."""\n            console = Console()\n            console.clear()\n            console.show_cursor(False)\n            airmon = pyrcrack.AirmonNg()\n\n            interface = Prompt.ask(\n                \'Select an interface\',\n                choices=[a[\'interface\'] for a in await airmon.interfaces])\n\n            async with airmon(interface) as mon:\n                async with pyrcrack.AirodumpNg() as pdump:\n                    async for result in pdump(mon.monitor_interface):\n                        console.clear()\n                        console.print(result.table)\n                        await asyncio.sleep(2)\n\n\n        asyncio.run(scan_for_targets())\n\nThis snippet of code will produce the following results:\n\n.. image:: https://raw.githubusercontent.com/XayOn/pyrcrack/master/docs/scan.png\n',
    'author': 'David Francos',
    'author_email': 'opensource@davidfrancos.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
