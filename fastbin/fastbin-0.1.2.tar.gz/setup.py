# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fastbin']

package_data = \
{'': ['*']}

install_requires = \
['casbin>=0.8.4,<0.9.0']

setup_kwargs = {
    'name': 'fastbin',
    'version': '0.1.2',
    'description': 'Performance orientated improvements to pycasbin',
    'long_description': '#Fastbin\n\n[![codecov](https://codecov.io/gh/wakemaster39/fastbin/branch/master/graph/badge.svg?token=H9WAVWZ7YY)](undefined)\n[![Actions Status](https://github.com/wakemaster39/fastbin/workflows/Tests/badge.svg)](https://github.comwakemaster39/fastbin/actions)\n[![Version](https://img.shields.io/pypi/v/fastbin)](https://pypi.org/project/fastbin/)\n[![PyPI - Wheel](https://img.shields.io/pypi/wheel/fastbin.svg)](https://pypi.org/project/fastbin/)\n[![Pyversions](https://img.shields.io/pypi/pyversions/fastbin.svg)](https://pypi.org/project/fastbin/)\n\n_Fastbin_ is a drop in replacement of [pycasbin](https://github.com/casbin/pycasbin) the python implementation of the\ngreat authorization management [casbin](https://github.com/casbin/casbin).\n\n_Fastbin_ is designed to address the primary concern when working with large sets of rules; Performance.\n\nThe root cause of working with large rule sets is the following: https://github.com/casbin/pycasbin/blob/88bcf96eb0586acd5a2cf3d3bd22a7802a0bfb27/casbin/core_enforcer.py#L238\n\nIterating over 10,000 rules to get a yes or no answer takes time, there really isn\'t a way around the fact. This limitation\ncomes from the generalization that casbin attempts to support. Independent on the format of your request, or policy definition\ncasbin if able to support your authorization mechanism.\n\n_Fastbin_ makes a minimal set of assumptions to allow efficient filtering of the model so that the number of rules you\nare iterating over to get a result is much smaller and performance can be maintained. Using _Fastbin_ when working with\nrule sets of any size, it is possible to keep resolution of enforcement sub millisecond.\n\n## Usage\nAssuming your model and policies meet the requirements discussed [below](#required-assumptions), to use _Fastbin_\nit takes the same arguments as the standard enforcer with additionally taking an ordered list of integers\nrepresenting the index position for a rule that should used to enable the cache.\n\n_Fastbin_ used a nested dictionary structure to manage its cache, it based on the assumption that keys are exact matches\nand can be used to filter on. For example, if you have rules that follow a similar format to `["/user99", "/obj99999", "read"]`,\nand a matcher of `m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act` we can say that if we pre-filtered out all rules\nthat the objects or the action didn\'t match we would have a much smaller ruleset to manage.\n\nRather iterating on all the rules knowing the majority will not pass the `r.obj == p.obj && r.act == p.act` of the matcher,\nwe can tell _Fastbin_ to cache the rules based on `obj` and then the `action`. Then when it comes to enforcing a rule,\n_Fastbin_ uses the incoming data to filter down the policies down to the minimal number based on the cache and\nthen then rest of the normal casbin enforcement logic takes place.\n\n```python\n"""\n# Request definition\n[request_definition]\nr = sub, obj, act\n\n# Policy definition\n[policy_definition]\np = sub, obj, act\n"""\n\nimport time\n\nfrom fastbin import FastEnforcer\n\nadapter = "/path/to/adapter" # or adapter of your choice\nenforcer = FastEnforcer([1,2], "/path/to/model", adapter)\n\nfor x in range(100):\n    for y in range(100000):\n        enforcer.add_policy(f"/user{x}", f"/obj{y}", "read")\n\n\ns = time.time()\n# this is the absolute worst case last entry and should require iterating 10M rows and be very slow\na = enforcer.enforce("/user99", "/obj99999", "read")\nprint(a, (time.time() - s) * 1000)\n\n# Output:\n# True 0.8349418640136719\n```\n\n## Required Assumptions\n\n The two assumptions that are\nrequired are:\n\n* The order of the fields in the request and the policy to be used in the cache are at the same index position\n\nValid Rule Sets:\n```\n# Request definition\n[request_definition]\nr = sub, obj, act\n\n# Policy definition\n[policy_definition]\np = sub, obj, act\n```\n```\n# Request definition\n[request_definition]\nr = sub, obj, act\n\n# Policy definition\n[policy_definition]\np = sub, obj, act, protected, before\n```\n\nInvalid Rul Sets:\n```\n# Request definition\n[request_definition]\nr = sub, obj, act\n\n# Policy definition\n[policy_definition]\np = sub, act, obj  # Not the act, obj have been swapped\n```\n```\n# Request definition\n[request_definition]\nr = sub, obj, act\n\n# Policy definition\n[policy_definition]\np = sub, obj, protected, before, act # There are extra keys between the values\n```\n\n* The keys being used to cache do not require processing to extract from the cache.\n\nSome people attempt to shrink the size of their rule sets but combing rules by using patterns in their rules such as setting\nthe action to be `read,write` and using a regex to split and match these values. This is not supported by _Fastbin_ and\nis actually an anti-pattern now as you will be loosing performance.\n\n\n### Why Not Filtered Policies?\n\nFiltered policies are highly recommended and should be used in conjunction with _Fastbin_. _Fastbin_ is great at helping\nworking with large rule sets, but it cannot aid in the loading of those large policies from disk. This is where\nloading filter policies really helps. If you can take you 1 million entry rule set, and shrink down the possible rules\nyou care about down to 1-10 thousand rules that can load in a reasonable amount of time, _Fastbin_ will then help\nensure enforcement against these rules is fast as well.\n\n\n## Contributing\n\n```\npoetry run pre-commit install -t pre-commit -t commit-msg && poetry run pre-commit autoupdate && poetry run pre-commit run --all\n```\n',
    'author': 'Cameron Hurst',
    'author_email': 'cameron.a.hurst@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wakemaster39/fastbin',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
