# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yfs']

package_data = \
{'': ['*']}

install_requires = \
['enlighten>=1.6.2,<2.0.0',
 'loguru>=0.5.2,<0.6.0',
 'more_itertools>=8.5.0,<9.0.0',
 'pandas>=1.1.2,<2.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'prompt-toolkit>=3.0.7,<4.0.0',
 'pydantic>=1.6.1,<2.0.0',
 'python-decouple>=3.3,<4.0',
 'requests-html>=0.10.0,<0.11.0',
 'requests[socks]>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'yfs',
    'version': '0.3.0',
    'description': 'Scrape Yahoo Finance',
    'long_description': '# YFS\n## Yahoo Finance Scraper with a WYSIWYG approach.\n[![Travis (.org)](https://img.shields.io/travis/dgnsrekt/yfs?style=for-the-badge&logo=appveyor?url=)](https://travis-ci.com/dgnsrekt/yfs)\n[![Black](https://img.shields.io/badge/code%20style-black-black?style=for-the-badge&logo=appveyor)](https://github.com/psf/black)\n[![GitHub](https://img.shields.io/github/license/dgnsrekt/yfs?style=for-the-badge)](https://raw.githubusercontent.com/dgnsrekt/yfs/master/LICENSE)\n\nWant to scrape data from the summary page use the get_summary_page function. Want to scrape the summary pages of a list of symbols use the get_multiple_summary_pages function. The returned object can be serialized with .json, .dict, ***and depending on the object .dataframe*** methods. Each function can accept a proxy to help avoid rate limiting. In fact in the future you can install [requests-whaor](https://github.com/dgnsrekt/requests-whaor) ***ANOTHER WORK IN PROGRESS*** which supplies a rotating proxy to bypass rate limits.\n\n***Before you start please note adding historical data to this API is not a priority. At some point I will get around to it. My main focus are options, quote information and symbol lookup. So please do not raise issues about historical data.***\n\n## Features\n* [x] Company and Symbol lookup\n* [x] Summary Page\n* [x] Option Chains\n* [x] Statistics Page\n\n## [>> To the documentation.](https://dgnsrekt.github.io/yfs/)\n\n## Quick Start\n\n### Prereqs\n* Python ^3.8\n\n### Install with pip\n```\npip install yfs\n```\n\n### Install with [poetry](https://python-poetry.org/)\n```\npoetry add yfs\n```\n\n### How to scrape multiple summary pages from yahoo finance.\n```python\nfrom yfs import get_multiple_summary_pages\n\nsearch_items = ["Apple", "tsla", "Microsoft", "AMZN"]\n\nsummary_results = get_multiple_summary_pages(search_items)\nfor page in summary_results:\n    print(page.json(indent=4))\n    break  # To shorten up the quick-start output.\n\nCOLUMNS = [\n    "close",\n    "change",\n    "percent_change",\n    "average_volume",\n    "market_cap",\n    "earnings_date",\n]\nprint(summary_results.dataframe[COLUMNS])\n\n```\nOutput\n```python\n➜ python3 quick_start_example.py\nDownloading Summary Data... 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 4/4 [00:03<00:00, 1.19 symbols/s]{\n    "symbol": "AAPL",\n    "name": "Apple Inc.",\n    "quote": {\n        "name": "Apple Inc.",\n        "close": 113.02,\n        "change": -3.77,\n        "percent_change": -3.23\n    },\n    "open": 112.89,\n    "high": 112.22,\n    "low": 115.37,\n    "close": 113.02,\n    "change": -3.77,\n    "percent_change": -3.23,\n    "previous_close": 116.79,\n    "bid_price": 112.58,\n    "bid_size": 800,\n    "ask_price": 112.77,\n    "ask_size": 3000,\n    "fifty_two_week_low": 137.98,\n    "fifty_two_week_high": 53.15,\n    "volume": 144711986,\n    "average_volume": 172065562,\n    "market_cap": 1933000000000,\n    "beta_five_year_monthly": 1.28,\n    "pe_ratio_ttm": 34.29,\n    "eps_ttm": 3.3,\n    "earnings_date": "2020-10-28",\n    "forward_dividend_yield": 0.82,\n    "forward_dividend_yield_percentage": 0.7,\n    "exdividend_date": "2020-08-07",\n    "one_year_target_est": 119.24\n}\n          close  change  percent_change  average_volume     market_cap earnings_date\nsymbol\nAAPL     113.02   -3.77           -3.23       172065562  1933000000000    2020-10-28\nAMZN    3125.00  -96.26           -2.99         5071692  1565000000000    2020-10-29\nMSFT     206.19   -6.27           -2.95        34844893  1560000000000    2020-10-21\nTSLA     415.09  -33.07           -7.38        80574089   386785000000    2020-10-21\n```\n### Next step [fuzzy search examples](https://dgnsrekt.github.io/yfs/examples/fuzzy-search-examples/)\n\n## TODO\n* [ ] More testing\n* [ ] More Docs\n* [ ] More examples\n* [ ] [WHAOR](https://github.com/dgnsrekt/requests-whaor) Example\n* [ ] Profile Page\n* [ ] Financials Page\n* [ ] Analysis Page\n* [ ] Holders page\n* [ ] Sustainability Page\n* [ ] Historical Page\n* [ ] Chart Page\n* [ ] Conversations Page maybe ¯\\_(ツ)_/¯\n\n## Contact Information\nTelegram = Twitter = Tradingview = Discord = @dgnsrekt\n\nEmail = dgnsrekt@pm.me\n',
    'author': 'dgnsrekt',
    'author_email': 'dgnsrekt@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://dgnsrekt.github.io/yfs/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
