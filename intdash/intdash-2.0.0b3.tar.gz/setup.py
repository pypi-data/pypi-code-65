from setuptools import find_packages, setup
import os
import re


ROOT = os.path.dirname(__file__)
VERSION_RE = re.compile(r'''__version__ = ['"]v([0-9.a-z]+)['"]''')

def get_version():
    init = open(os.path.join(ROOT, "intdash", "__init__.py")).read()
    return VERSION_RE.search(init).group(1)


DESCRIPTION="intdash SDK for Python"
LONG_DESCRIPTION= """
intdash SDK for Python is a client library that accesses the intdash resource API and real-time API.

## Install

You can install intdash SDK for Python (hereafter intdash-py) using PyPI. Install with the following command.

```
$ pip install intdash
```

## Usage

To start using intdash-py, create a client. To create a client, use the URL of the connection destination and the credentials of the edge account (token or user name/password combination). See intdash client for other available parameters.

```python
import intdash

client = intdash.Client(
    url = "https://example.intdash.jp",
    edge_token = "your_token",
)
```

Example:   
the edge resource is specified and the information of the own edge is retrieved.

```python
# Edge resource
edges = client.edges

# print out edge information
me = edges.me()
print(me)
```

## Documentation 

Documentation and links to additional resources are available at https://docs.intdash.jp/sdk/python/latest/en/

"""

setup(
    name="intdash",
    version=get_version(),
    packages=find_packages(exclude=['tests']),
    python_requires=">=3.5",
    url="https://docs.intdash.jp/sdk/python/latest/en/",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    install_requires=[
        "numpy",
        "pandas",
        "requests",
        "tornado",
        "debtcollector",
        "protobuf",
    ],
    author='aptpod,Inc',
    author_email='sdk-support@aptpod.co.jp',
    keywords='intdash, intdash SDK',
    license="Apache License 2.0",
)
