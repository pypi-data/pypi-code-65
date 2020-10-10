# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['matt']

package_data = \
{'': ['*']}

install_requires = \
['pyxdg>=0.26,<0.27', 'termcolor>=1.1.0,<2.0.0']

extras_require = \
{':sys_platform == "win32"': ['colorama>=0.4.3,<0.5.0']}

setup_kwargs = {
    'name': 'matt',
    'version': '0.2.0',
    'description': 'A maths test',
    'long_description': '# Matt\nMatt is a free software (licensed under the [GNU GPL v3 (or later)](https://www.gnu.org/licenses/gpl-3.0.html)) maths test program.\n"Matt" (or "MATT") is a recursive acronym for "MATT Arithmetic Training Test".\n\n## Installation\nMatt depends on:\n\n* [termcolor](https://pypi.org/project/termcolor/)\n\n* [pyxdg](https://www.freedesktop.org/wiki/Software/pyxdg/)\n\n* [colorama](https://pypi.org/project/colorama/) (windows only)\n\nThere are 2 methods of installation: via poetry and via pip:\n\n### Installation via [poetry](https://python-poetry.org/)\nPoetry should handle the installation of dependencies.\nTo install, first clone the git repository, then run:\n```sh\npoetry install\n```\n\n### Installation via pip\nPip should handle the installation of dependencies.\nTo install, run:\n```sh\npython3 -m pip install matt\n```\n\n## Usage\nRun `python3 -m matt -h` for help.\nMatt accepts the following arguments:\n\n * `--difficulty` or `-d` to set the difficulty (in the format "\\<namespace\\>:\\<number\\>").\n   The `default` namespace is reserved for the default difficulties.\n   If unspecified the default is `default:1`.\n\n* `--operations` or `-o` to set the available operations.\n   Operations are separated by commas, the available operations are:\n   - `+`: Addition\n   - `-`: Subtraction\n   - `*`: Multiplication\n   - `/`: Division\n\n   One can also use custom operators defined in the configuration.\n\n   Example: `-o +,-` to enable only addition and subtraction.\n\n* `--minimum` or `-m` to set the minumum, default (if not specified in difficulty): 0.\n\n* `--maximum` or `-M` to set the maximum, default (if not specified in difficulty): 10.\n\n* `--question-amount` or `-q` to set the amount of questions, the default is 10.\n\nNOTE: The maximum must be more than the minimum.\n\n## Config\nMatt has a configuration file, it is written in Python,\nand located at `$XDG_CONFIG_HOME/matt/config.py`.\nBy default `$XDG_CONFIG_HOME` is set to `~/.config`,\nso if you have not set it then it is probably `~/.config/matt/config.py`.\n\nThe configuration can define custom difficulties and custom operations.\n\nMatt\'s builtin difficulties/operations are defined in `matt/defaults.py`,\nand they are defined in the same way as custom ones so you can look there for further examples\nand details on Matt\'s defaults.\n\n### Defining custom difficulties\nThe configuration can provide a `difficulty` function that accepts 2 parameters:\n\n* `namespace` (str): The namespace of the difficulty.\n\n* ``number`` (int): The number of the difficulty.\n\nThe ``difficulty`` function must return a dict or None (although if it simply returns None then it is useless).\n\nThe dict can have the following keys:\n\n* `minimum` (int): the minimum number\n\n* `maximum` (int): the maximum number\n\n* `operations` (a list of strs (`typing.List[str]`)): a list of allowed operations\n\nA simple example is:\n```python\nfrom typing import Union\n\n\ndef difficulty(namespace: str, number: int) -> Union[dict, None]:\n    if namespace == "manual":\n       if number == 1:\n           return {\n               "operations": ["+", "-"],\n               "maximum": 20,\n               "minimum": 10\n           }\n    return None\n```\n\nIt is also possible to create a dynamic maximum,\nlike the following example, which creates a difficulty called "automatic",\nwhose maximum is the number * 10:\n```python\nfrom typing import Union\n\n\ndef difficulty(namespace: str, number: int) -> Union[dict, None]:\n    if namespace == "automatic":\n        return {\n            "operations": ["+", "-", "*", "/"],\n            "maximum": number * 10\n        }\n    return None\n```\n\n### Defining custom operations\nThe configuration can provide a `operations` dict to define custom operations.\nThe keys are the names of the operations,\nand the values are dicts which can contain the following keys:\n\n* `format` (function): a function which takes 2 numbers and returns a str.\n The str is usually a string which contains both values and the operation,\n it is used to ask the user about the answer.\n Unless `format_full_override` or `format_colour_override` are set to True,\n it is sent to the user prepended with `What is `, and appended with `? `.\n an example of a function used for `format` is (this example would be for the `+` operation):\n ```python\n lambda n1, n2: f"{n1} + {n2}"\n ```\n If this is not set then the default is `<n1> <operation> <n2>`.\n\n* `function` (function): a function which takes 2 numbers,\n and returns the correct answer for those 2 numbers. This must be defined.\n Example (for a strange operation that is the result of addition - 1):\n ```python\n lambda n1, n2: n1 + n2 - 1\n ```\n\n* `format_full_override` (bool): if this is True then `What is `/`? ` are not added to the string.\n\n* `format_colour_override` (bool): if this is True then the string is not coloured.\n\nAn example which defines an operation called `!` that is the result of addition -1,\nand an operation called `++` that is the same as addition but just gives the user the answer:\n```python\nfrom operator import add\n\noperations: dict = {\n    "!": {\n        "function": lambda n1, n2: n1 + n2 - 1\n    },\n    "++": {\n        "function": add,\n        "format": lambda n1, n2: f"Type {n1 + n2}! ",\n        "format_full_override": True\n    }\n}\n```\n',
    'author': 'Noisytoot',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://codeberg.org/noisytoot/matt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
