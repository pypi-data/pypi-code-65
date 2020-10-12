# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bmx']

package_data = \
{'': ['*']}

extras_require = \
{':python_version < "3.8"': ['singledispatchmethod']}

setup_kwargs = {
    'name': 'bmx',
    'version': '0.0.1',
    'description': 'Basic Markup eXpressions',
    'long_description': '# BMX - Basic Markup eXpressions\n\nA DSL for representing HTML/XML in Python using an expression-like syntax. Why? You get to use the Python syntax you already know.\n\n## Example\n<table>\n<tr>\n<td> Taking the example from the Jinja2 website: </td> <td> This can be represented in BMX like this: </td>\n</tr>\n<tr>\n\n<td>\n\n```html+jinja\n<!DOCTYPE html>\n<html lang="en">\n<head>\n  <title>My Webpage</title>\n</head>\n<body>\n  <ul id="navigation">\n  {% for item in navigation %}\n    <li>\n      <a href="{{ item.href }}">{{ item.caption }}</a>\n    </li>\n  {% endfor %}\n  </ul>\n\n  <h1>My Webpage</h1>\n  {{ a_variable }}\n\n  {# a comment #}\n</body>\n</html>\n```\n\n</td>\n\n<td>\n\n ```Python\nmydoc = (\n  DOCTYPE(\'html\')\n  +html(lang=\'en\') \n    +head\n      +title +"My Webpage" -title\n    -head\n    +body\n      +ul(\'#navigation\') +(\n        +li\n          +a(href=item.href) +item.caption -a\n        -li\n        for item in navigation)\n      -ul\n\n      +h1 +"My Webpage" -h1\n      +a_variable\n\n      # a comment\n    -body\n  -html)\n```\n\n</td>\n</tr>\n</table>\n\n**Note:** Just as with ordinary Python expressions, multi-line BMX expressions must be surrounded by parentheses. \n\n## How does it work?\nWe define a `Tag` class which overrides the unary +/- and binary +/- operators to model the opening and closing tags of HTML. We provide a `__call__` method to model HTML attributes as keyword arguments and a `__getattr__` method to provide a shorthand for HTML classes (see below). A `Tag` is instantiated for every HTML tag and is available with a `from bmx.htmltags import html, head, body, span`.\n\n## Usage\nAn example using Flask (available in the top-level source directory):\n```Python\n# flask_greeter.py\nfrom bmx.htmltags import (\n    html, \n    head, \n    title,\n    body,\n    p\n)\nfrom flask import Flask\n\napp = Flask(__name__)\n\n@app.route(\'/<name>\')\ndef greeter(name: str):\n    return str(\n        # fmt: off\n        +html\n          +head\n            +title +"Flask Greeter" -title\n          -head\n          +body\n            +p +f"Hello {name}" -p\n          -body\n        -html\n        # fmt: on\n    )\n```\n\nInstall Flask then  run it as:\n```Shell\nFLASK_APP=flask_greeter.py flask run\n```\n\nGo to `https://127.0.0.1:5000/<your_name>` in your browser (eg. `https://127.0.0.1:5000/Stuart`) and you will see the message.\n\n## Table of Conversions\n\n|Type   |HTML       |BMX |Comment/Mnemonic|\n|-------|-----------|----|----------------|\n|Opening tag | `<div>` | `+div` |*Mnemonic: Adding content*|\n|Closing tag | `</div>` | `-div` |*Mnemonic: opposite of adding content*  |\n|Self-closing tag | `<input/>` | `+input` | Self-closing tag are pre-defined |\n|Attributes | `<input type="text">` | `+input_(type_="text")` | *Mnemonic: attributes are keyword arguments.* **Note**: Append an underscore to avoid conflicts with Python keywords |\n|Attributes: shorthand for `id` and `class`| `<div id="userinput" class="credentials" >` | `+div(\'#userinput.credentials\')` | *#id* *.classname* |\n|Attributes: shorthand for `class`| `<div class="col-sm-8 col-md-7 py-4">` | `+div .col_sm_8 .col_md_7 .py_4` | *.classname* Underscores are transposed to dashes |\n|Composing tags and content| `<h1>The Title</h1>`| `+h1 +"The Title" -h1` | *Mnemonic: think string concatenation ie. "Hello " + "World!"*|\n\n## Autoformatters\n\n### Black\nTo use the Black uncompromising autoformatter, surround your BMX markup with `#fmt: off` and `#fmt: on` comments like this:\n```Python\nresult = (\n    # fmt: off\n    +html\n        +body\n            +h1 +"My Page" -h1\n        -body\n    -html\n    # fmt: on\n)\n```\n\n### Autopep8\nTo use autopep8, you can use the `#fmt: off` and `#fmt: on` comments as above or turn off 2 fixes:\n* E225 - Fix missing whitespace around operator.\n* E131 - Fix hanging indent for unaligned continuation line.\n\nwhereever you put your autopep8 [configuration](https://github.com/hhatto/autopep8#configuration)\n```INI\nignore = E225,E131\n```\n',
    'author': 'Stuart Pullinger',
    'author_email': 'stuartpullinger@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/stuartpullinger/bmx',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
