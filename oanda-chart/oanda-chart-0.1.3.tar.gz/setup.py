# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oanda_chart',
 'oanda_chart.env',
 'oanda_chart.selectors',
 'oanda_chart.util',
 'oanda_chart.widgets']

package_data = \
{'': ['*'], 'oanda_chart': ['geo/*', 'image_data/*']}

install_requires = \
['forex-types>=0.0.6,<0.0.7',
 'oanda-candles>=0.1.0,<0.2.0',
 'tk-oddbox>=0.0.3,<0.0.4']

setup_kwargs = {
    'name': 'oanda-chart',
    'version': '0.1.3',
    'description': 'Oanda forex candle chart tkinter widget.',
    'long_description': '# oanda-chart\nOanda forex candle chart tkinter widget.\n\n# Video Demo\n[YouTube demo of chart widget](https://youtu.be/rPa5l9m_QI8)\n\n#### Quick Sample of Usage\nThis code is a complete script for a working chart provided that:\n1. There is a working internet connection.\n1. An `OANDA_TOKEN` environmental variable is set to a valid access token.\n```python\nimport tkinter\nimport os\n\nfrom oanda_chart import ChartManager\n\nroot = tkinter.Tk()\nmanager = ChartManager(os.getenv("OANDA_TOKEN"))\nchart = manager.create_chart(root, flags=True, width=700, height=400)\nchart.grid(row=0, column=0, sticky="nsew")\nroot.rowconfigure(0, weight=1)\nroot.columnconfigure(0, weight=1)\nroot.mainloop()\n```\n\n#### Some Background\nThe charts rely on the [oanda-candles](https://pypi.org/project/oanda-candles/)\npackage which pulls candles from [Oanda](http://oanda.com) through their\n[V20 Restful API](http://developer.oanda.com/rest-live-v20/introduction/) The user must supply a\nsecret token string that is associated with either a demo or real brokerage account with\nOanda.\n\n### Feature Summary\n1. This is strictly for tkinter applications.\n1. Only Oanda Forex candles are charted.\n1. User must supply a secret access token to their Oanda account.\n1. By dragging on chart user can pan about and candles are downloaded automatically as needed.\n1. Chart automatically keeps candles up to date with checks for recent prices every 5 seconds.\n1. Panning around can be done both in and out of a mode where the candles are adjusted to fit view.\n1. Dragging mouse on price scale makes candles taller or shorter. \n1. Dragging mouse on time scale makes them fatter or narrower (and so does mouse wheel).\n1. An optional Pair (instrument) selector with flags matching currency is an option for the chart.\n1. Pair (instruments) are also selectable from drop down.\n1. Granularity of candles (e.g. Monthly, hourly, etc) are limited to certain values supported by Oanda\'s V20 API.\n1. Bid, Mid, or Ask price can be selected for (default is Bid).\n1. All the selectors can be linked to one of several colors to enable changing a pair for one chart to also change it for others and such.\n\n### Some Missing Features\nSome features a trader might expect of a candle applications but which are presently missing:\n1. There are no annotations supported yet (no putting lines, or text, etc in chart).\n1. There is not selection mechanism for candles to see stats on them specifically.\n1. There is no way to place an order or see your order info.\n1. There are no indicators other than the candles.\n\n',
    'author': 'Andrew Allaire',
    'author_email': 'andrew.allaire@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aallaire/oanda-chart',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
