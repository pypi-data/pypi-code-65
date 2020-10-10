# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ciphit',
 'ciphit.basemods',
 'ciphit.basemods.Ciphers',
 'ciphit.basemods.Crypto',
 'ciphit.legacy']

package_data = \
{'': ['*']}

install_requires = \
['click-option-group>=0.5.1,<0.6.0',
 'click>=7.1.2,<8.0.0',
 'cryptography>=2.8,<3.0',
 'rich>=8.0.0,<9.0.0']

entry_points = \
{'console_scripts': ['ciphit = ciphit.ciphit:main']}

setup_kwargs = {
    'name': 'ciphit',
    'version': '0.6.0',
    'description': 'A cryptography cli-tool',
    'long_description': '<p align="center">\n<a href="https://github.com/sgrkmr/ciphit"><img alt="Ciphit" src="https://user-images.githubusercontent.com/57829219/84270533-7492e380-ab48-11ea-9270-8531ea72ac6e.png"></a>\n</p>\n\n<p align="center">\n<a href="https://pypi.org/project/ciphit/"><img alt="PyPi" src="https://img.shields.io/pypi/v/ciphit.svg"></a>\n<a href="https://pypi.org/project/ciphit/"><img alt="Downloads" src="https://pepy.tech/badge/ciphit"></a>\n<a href="https://github.com/sgrkmr/ciphit/commits/master"><img alt="Commits" src="https://img.shields.io/github/last-commit/sgrkmr/ciphit"></a>\n<a href="https://www.python.org/downloads/release/python-374/"><img alt="python3" src="https://img.shields.io/badge/Python-3.7-blue"></a>\n<a href="https://GitHub.com/sgrkmr/ciphit/graphs/contributors/"><img alt="Contributors" src="https://img.shields.io/github/contributors/sgrkmr/ciphit.svg"></a>\n<a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/github/license/sgrkmr/ciphit.svg"></a>\n</p>\n\n<p align="center">\n<code>ciphit</code> is a basic cryptography cli-tool, Currently only supports AES-CBC.\n</p>\n\n---\n<!--\n# Screenshots\n![scrn](https://user-images.githubusercontent.com/57829219/84272798-81fd9d00-ab4b-11ea-89e2-c712a16c00a3.png)\n-->\n\n## Installation and Usage\n### Installation\n\n_ciphit_ can be installed by running `pip install ciphit`.\n\n#### Install from GitHub\n\nIf you want to install from GitHub, use:\n\n`pip install git+git://github.com/sgrkmr/ciphit`\n\n### Usage\n\n### Command line options\n\nCurrently _ciphit_ doesn\'t provide many options. You can list them by running `ciphit --help`:\n\n```text\nUsage: ciphit [OPTIONS]\n\nOptions:\n  Encode/Decode: [mutually_exclusive, required]\n    -e, --encode\n    -d, --decode\n    --edit                        To edit Encrypted/Encoded files created by\n                                  ciphit.\n\n  -k, --key TEXT                  The key with which text is Encoded/Decoded.\n  Text/File: [mutually_exclusive]\n    -t, --text TEXT               The text you want to Encode/Decode.\n    -f, --file FILENAME\n  --help                          Show this message and exit.\n```\n\n<p><b>Make sure you run these commands in Terminal/CMD or any other shell you use.</b></p>\n\n## Examples\n\nSame commands in _ciphit_ can be used in different variants, for eg:\n\n### Decoding `-d`/`--decode`\n\n- Passing all parameters, i.e. `-k` for _key_, `-t` for _text_\n\n```console\n$ ciphit -dk password -t "BAxEtd2AO8EGuqIbmVbFQwABhqCAAAAAAF9-z7EjDVV13bKOTLIF-FDXF921sNfGhnSShod4CFHezycHLXQ08AqvBwQoT1zmOd9jt2gZf3VBSHyzfyrsdnvnQ-r5jJPpUKHTlWsZ7i-CW10LmhHzfsBXuQ7b9A4E5DD4EtY="\nFinal result: Just so you know, this is a text.\n```\n\n- Passing only _text_\n\n```console\n$ ciphit -dt "BAxEtd2AO8EGuqIbmVbFQwABhqCAAAAAAF9-z7EjDVV13bKOTLIF-FDXF921sNfGhnSShod4CFHezycHLXQ08AqvBwQoT1zmOd9jt2gZf3VBSHyzfyrsdnvnQ-r5jJPpUKHTlWsZ7i-CW10LmhHzfsBXuQ7b9A4E5DD4EtY="\nKey:\nRepeat for confirmation:\nFinal result: Just so you know, this is a text.\n```\n\n- **OR** You can just pass `-d`/`--decode`, other parameters will be asked as a prompt:\n\n```console\n$ ciphit -d\nKey:\nRepeat for confirmation:\nOpening editor # Enter the ciphered text in editor then save & exit.\nPress any key to continue ...\nFinal result: Just so you know, this is a text.\n```\n\nSimilarly other commands can be used.\n\n## License\nLicensed under [MIT](https://opensource.org/licenses/MIT).\n',
    'author': 'Sagar Kumar',
    'author_email': '57829219+sgrkmr@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sgrkmr/ciphit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
