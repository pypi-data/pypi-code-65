# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bing_image_urls']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.15.5,<0.16.0', 'logzero>=1.5.0,<2.0.0']

setup_kwargs = {
    'name': 'bing-image-urls',
    'version': '0.1.3',
    'description': 'fetch bing image urls based on keywords',
    'long_description': '# Bing-Image-Urls ![build](https://github.com/ffreemt/bing-image-urls/workflows/build/badge.svg)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/bing-image-urls.svg)](https://badge.fury.io/py/bing-image-urls)\n\nFetch Bing image urls based on keywords\n\n### Installation\n```pip install bing-image-urls```\n\n### Usage\n\n```python\n\nfrom bing_image_urls import bing_image_urls\n\nprint(bing_iamge_urls("bear", limit=2))\n# [\'https://www.stgeorgeutah.com/wp-content/uploads/2017/01/blackbear.jpg\',\n# \'http://www.cariboutrailoutfitters.com/wp-content/uploads/2017/03/saskatchewan-black-bear-hunting.jpg\']\n```\n\nThe helper function `get_image_size` may sometimes come handy if you need to know the size of the image. `get_image_size` takes a filename or a filelike object as input and outputs the widht and height of the image. Hence the raw bytes of an image from the net can be wrapped in io.BytesIO and fed to `get_image_size`.\n\n```python\nimport io\nimport httpx\nfrom bing_image_urls import get_image_size\n\nurl = "https://www.stgeorgeutah.com/wp-content/uploads/2017/01/blackbear.jpg"\ntry:\n    resp = httpx.get(url)\n    resp.raise_for_status()\nexcept Exception as exc:\n    raise SystemExit(exc)\n\nprint(get_image_size(io.BytesIO(resp.content)))\n# (1797, 2696)\n```\n\nMost the code in `get_image_size` is from [imagesize_py](https://github.com/shibukawa/imagesize_py). As soon as the [PR](https://github.com/shibukawa/imagesize_py/pull/46) about filelike object is merged to the main, the `imagesize_py` package will be included as a depdendant package.\n',
    'author': 'ffreemt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffreemt/bing-image-urls',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
