# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['a2wsgi']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'a2wsgi',
    'version': '1.1.0',
    'description': 'Convert WSGI app to ASGI app or ASGI app to WSGI app.',
    'long_description': '# a2wsgi\n\nConvert WSGI app to ASGI app or ASGI app to WSGI app.\n\nPure Python. No dependencies.\n\n## Install\n\n```\npip install a2wsgi\n```\n\n## How to use\n\nConvert WSGI app to ASGI app:\n\n```python\nfrom a2wsgi import WSGIMiddleware\n\nASGI_APP = WSGIMiddleware(WSGI_APP)\n```\n\nConvert ASGI app to WSGI app:\n\n```python\nfrom a2wsgi import ASGIMiddleware\n\nWSGI_APP = ASGIMiddleware(ASGI_APP)\n```\n\n## Benchmark\n\nRun `pytest ./benchmark.py -s` to compare the performance of `a2wsgi` and `uvicorn.middleware.wsgi.WSGIMiddleware` / `asgiref.wsgi.WsgiToAsgi`.\n\n## Why a2wsgi\n\n### Convert WSGI app to ASGI app\n\nThe performance of uvicorn-WSGIMiddleware is higher than a2wsgi. However, when dealing with large file uploads, it is easy to cause insufficient memory [uvicorn/issue#371](https://github.com/encode/uvicorn/issues/371). a2wsgi uses `asyncio.run_coroutine_threadsafe` to regulate the pace of reading data, thus solving this problem.\n\n### Convert ASGI app to WSGI app\n\nThe HTTP trigger of Alibaba Cloud Serverless supports the WSGI interface but not the ASGI interface, which is very useful for deploying starlette/index.py to such services.\n',
    'author': 'abersheeran',
    'author_email': 'me@abersheeran.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/abersheeran/a2wsgi',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
