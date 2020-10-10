# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['borisat', 'borisat.apis', 'borisat.models', 'borisat.models.rd']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.5.3,<0.6.0',
 'pydantic>=1.6.1,<2.0.0',
 'stringcase>=1.2.0,<2.0.0',
 'zeep>=3.4.0,<4.0.0']

setup_kwargs = {
    'name': 'borisat',
    'version': '1.0.0',
    'description': 'a python library for retrieving company public data in thailand. It has its own public database for caching, so, it is really fast, smart, and save lot of time and energy.',
    'long_description': '# borisat\na python library for retrieving company public data in thailand. It has its own public database for caching, so, it is really fast, smart, and save lot of time and energy.\n\n## Get Started\n```shell\npip install borisat\n```\n\n```python\nimport borisat\n\na_valid_tax_id = tax_id = \'0105558096348\'\n\nif borisat.is_exist(tax_id):\n    company = borisat.get_info(tax_id=tax_id) \n    print(company)\n# NID=\'0105558096348\' title_name=\'บริษัท\' name=\'โฟลว์แอคเคาท์ จำกัด\' surname=\'-\' branch_name=\'โฟลว์แอคเคาท์ จำกัด\' branch_number=0 branch_title_name=\'บริษัท\' business_first_date=\'2016/04/07\' building_name=\'ชุดสกุลไทย สุรวงศ์ ทาวเวอร์\' floor_number=\'11\' room_number=\'12B\' village_name=\'-\' house_number=\'141/12\' moo_number=\'-\' soi_name=\'-\' street_name=\'สุรวงศ์\' thambol=\'สุริยวงศ์\' amphur=\'บางรัก\' province=\'กรุงเทพมหานคร\' post_code=\'10500\'\n\nanother_valid_tax_id = tax_id = "0994000160097"\ncompany = borisat.get_info(tax_id=tax_id) \nprint(company)\n# NID=\'0994000160097\' title_name=\'มหาวิทยาลัย\' name=\'เทคโนโลยีพระจอมเกล้าธนบุรี\' surname=\'-\' branch_name=\'กลุ่มงานส่งเสริมและบริการวิจัย\' branch_number=0 branch_title_name=\'-\' business_first_date=\'2013/09/17\' building_name=\'สำนักงานอธิการบดี\' floor_number=\'-\' room_number=\'-\' village_name=\'-\' house_number=\'126\' moo_number=\'-\' soi_name=\'-\' street_name=\'ประชาอุทิศ\' thambol=\'บางมด\' amphur=\'ทุ่งครุ\' province=\'กรุงเทพมหานคร\' post_code=\'10140\'\n```\n\n## Why it is the way it is?\n0. [the government public api is obsolete, doc is unclear and this is 2020, and it is SOAP api. OMG](https://github.com/CircleOnCircles/rd_soap). thus, we need some kinds of modern interface.\n1. [retriving data from the government public api is F\\*\\*king slow in the business hours](https://github.com/CircleOnCircles/rd_soap). thus, we need some kinds of cache. a public one where who use this lib could enjoy.\n\n### A public cache?\nThere is no such thing as a public cache/database. There is a close thing.\n1. Public Google BigQuery\n2. Smart contact. Blockchain \n\nbeing a cache key value access is so critical. if you use BigQuery to query for a single row, since it is a column-based db in will cost a lot when your database get bigger, very costly. and to let other have your write-only key to the database is nut.\n\non surface Blockchain seems legit. there is a mapping data type on solidity. Wow, this might be a way to go. I took my word back when I saw a blog, [No, you don’t store data on the blockchain – here’s why](https://jaxenter.com/blockchain-data-164727.html) 1MB for 700 Dollars, holy cow! I knows that there is [a hashgraph blockchain](https://www.hedera.com/). the price is great, but there is no official python support + the unofficial is 2 years old of unmaintain.\n\nok then, my last combo would be create a cache serverless api + store on a serverless database which I pay myself and let the lib call my fast api first, if there is no data, call the gov server, then lib call my api to store the cache. open source everything that is my experiment.\n\n## Roadmap \n\nSee project board',
    'author': 'Nutchanon Ninyawee',
    'author_email': 'nutchanon@codustry.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CircleOnCircles/borisat',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
