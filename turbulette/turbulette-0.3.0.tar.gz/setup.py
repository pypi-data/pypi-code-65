# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['turbulette',
 'turbulette.apps',
 'turbulette.apps.auth',
 'turbulette.apps.auth.policy',
 'turbulette.apps.auth.resolvers',
 'turbulette.apps.auth.resolvers.queries',
 'turbulette.apps.base',
 'turbulette.apps.base.resolvers',
 'turbulette.conf',
 'turbulette.db',
 'turbulette.management',
 'turbulette.management.templates.app',
 'turbulette.management.templates.project',
 'turbulette.management.templates.project.alembic',
 'turbulette.middleware',
 'turbulette.test',
 'turbulette.type',
 'turbulette.validation']

package_data = \
{'': ['*'],
 'turbulette.apps.auth': ['graphql/queries/*', 'graphql/types/*'],
 'turbulette.apps.base': ['graphql/*'],
 'turbulette.management.templates.app': ['graphql/*', 'resolvers/*']}

install_requires = \
['alembic>=1.4.2,<2.0.0',
 'ariadne>=0.11,<0.13',
 'async-caches>=0.3.0,<0.4.0',
 'ciso8601>=2.1.3,<3.0.0',
 'click>=7.1.2,<8.0.0',
 'gino[starlette]>=1.0.1,<2.0.0',
 'passlib[bcrypt]>=1.7.2,<2.0.0',
 'psycopg2>=2.8.5,<3.0.0',
 'pydantic[email]>=1.6.1,<2.0.0',
 'python-jwt>=3.2.6,<4.0.0',
 'simple-settings>=0.19.1,<1.1.0']

extras_require = \
{'argon2': ['argon2-cffi>=20.1.0,<21.0.0']}

entry_points = \
{'console_scripts': ['turb = turbulette.management.cli:cli'],
 'pytest11': ['turbulette = turbulette.test.pytest_plugin']}

setup_kwargs = {
    'name': 'turbulette',
    'version': '0.3.0',
    'description': 'A batteries-included framework to build high performance, async GraphQL APIs',
    'long_description': '# Turbulette\n\n[![test](https://github.com/python-turbulette/turbulette/workflows/test/badge.svg)](https://github.com/python-turbulette/turbulette/actions?query=workflow%3Atest)\n[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/e244bb031e044079af419dabd40bb7fc)](https://www.codacy.com/gh/python-turbulette/turbulette/dashboard?utm_source=github.com&utm_medium=referral&utm_content=python-turbulette/turbulette&utm_campaign=Badge_Coverage)\n[![Codacy Badge](https://app.codacy.com/project/badge/Grade/e244bb031e044079af419dabd40bb7fc)](https://www.codacy.com/gh/python-turbulette/turbulette/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=python-turbulette/turbulette&amp;utm_campaign=Badge_Grade)\n![PyPI](https://img.shields.io/pypi/v/turbulette)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/turbulette)\n![PyPI - License](https://img.shields.io/pypi/l/Turbulette)\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n[![Generic badge](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)\n[![Generic badge](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n<p align="center">Turbulette packages all you need to build great GraphQL APIs :</p>\n\n<p align="center"><strong><em>ASGI framework, GraphQL library, ORM and data validation</em></strong></p>\n\n---\n\nDocumentation : [https://python-turbulette.github.io/turbulette/](https://python-turbulette.github.io/turbulette/)\n\n---\n\nFeatures :\n\n- Split your API in small, independent applications\n- Generate Pydantic models from GraphQL types\n- JWT authentication with refresh and fresh tokens\n- Declarative, powerful and extendable policy-based access control (PBAC)\n- Extendable auth user model with role management\n- Async caching (provided by async-caches)\n- Built-in CLI to manage project, apps, and DB migrations\n- Built-in pytest plugin to quickly test your resolvers\n- Settings management at project and app-level (thanks to simple-settings)\n- CSRF middleware\n- 100% test coverage\n- 100% typed, your IDE will thank you ;)\n- Handcrafted with ❤️, from 🇫🇷\n\n## Requirements\n\nPython 3.6+\n\n👍 Turbulette makes use of great tools/frameworks and wouldn\'t exist without them :\n\n- [Ariadne](https://ariadnegraphql.org/) - Schema-first GraphQL library\n- [Starlette](https://www.starlette.io/) - The little ASGI framework that shines\n- [GINO](https://python-gino.org/docs/en/master/index.html) - Lightweight, async ORM\n- [Pydantic](https://pydantic-docs.helpmanual.io/) - Powerful data validation with type annotations\n- [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html) - Lightweight database migration tool\n- [simple-settings](https://github.com/drgarcia1986/simple-settings) - A generic settings system inspired by Django\'s one\n- [async-caches](https://github.com/rafalp/async-caches) - Async caching library\n- [Click](https://palletsprojects.com/p/click/) - A "Command Line Interface Creation Kit"\n\n## Installation\n\n``` bash\npip install turbulette\n```\n\nYou will also need an ASGI server, such as [uvicorn](https://www.uvicorn.org/) :\n\n``` bash\npip install uvicorn\n```\n\n----\n\n## 🚀  5 min Quick Start\n\nHere is a short example that demonstrates a minimal project setup.\n\nWe will see how to scaffold a simple Turbulette project, create a Turbulette application, and write some GraphQL schema/resolver. It\'s advisable to start the project in a virtualenv to isolate your dependencies.\nHere we will be using [poetry](https://python-poetry.org/) :\n\n``` bash\npoetry init\n```\n\nThen, install Turbulette from PyPI :\n\n``` bash\npoetry add turbulette\n```\n\n### 1: Create a project\n\nFirst, create a `hello_world/` directory that will contain the whole project.\n\nNow, inside this folder, create your Turbulette project using the `turb` CLI :\n\n``` bash\nturb project my-project\n```\n\nYou should get with something like this :\n\n```console\n.\n└── 📁 my-project\n    ├── 📁 alembic\n    │   ├── 📄 env.py\n    │   └── 📄 script.py.mako\n    ├── 📄 .env\n    ├── 📄 alembic.ini\n    ├── 📄 app.py\n    └── 📄 settings.py\n```\n\nLet\'s break down the structure :\n\n- `📁 my-project` : Here is the so-called *Turbulette project* folder, it will contain applications and project-level configuration files\n- `📁 alembic` : Contains the [Alembic](https://alembic.sqlalchemy.org/en/latest/) scripts used when generating/applying DB migrations\n  - `📄 env.py`\n  - `📄 script.py.mako`\n- `📄 .env` : The actual project settings live here\n- `📄 app.py` : Your API entrypoint, it contains the ASGI app\n- `📄 settings.py` : Will load settings from `.env` file\n\n\nWhy have both `.env` and `settings.py`?\n\n\nYou don\'t *have to*. You can also put all your settings in `settings.py`.\nBut Turbulette encourage you to follow the [twelve-factor methodology](https://12factor.net),\nthat recommend to separate settings from code because config varies substantially across deploys, *code does not*.\nThis way, you can untrack `.env` from version control and only keep tracking `settings.py`, which will load settings\nfrom `.env` using Starlette\'s `Config` object.\n\n### 2: Create the first app\n\nNow it\'s time to create a Turbulette application!\n\nRun this command under the project directory (`my-project`) :\n\n```bash\nturb app --name hello-world\n```\n\nYou need to run `turb app` under the project dir because the CLI needs to access the `almebic.ini` file to create the initial database migration.\n\nYou should see your new app under the project folder :\n\n```console\n.\n└── 📁 my-project\n    ...\n    |\n    └── 📁 hello-world\n        ├── 📁 graphql\n        ├── 📁 migrations\n        │   └── 📄 20200926_1508_auto_ef7704f9741f_initial.py\n        ├── 📁 resolvers\n        └── 📄 models.py\n```\n\nDetails :\n\n- `📁 graphql` : All the GraphQL schema will live here\n- `📁 migrations` : Will contain database migrations generated by Alembic\n- `📁 resolvers` : Python package where you will write resolvers binded to the schema\n- `📄 models.py` : Will hold GINO models for this app\n\n### 3: GraphQL schema\n\nNow that we have our project scaffold, we can start writing actual schema/code.\n\nCreate a `schema.gql` file in the `📁 graphql` folder and add this base schema :\n\n``` graphql\nextend type Query {\n    user: [User]\n}\n\ntype User {\n    id: ID!\n    username: String!\n    gender: String!\n    isStaff: Boolean!\n}\n```\n\nNote that we *extend* the type `Query` because Turbulette already defines it. The same goes for `Mutation` type\n\n### 4: Add a resolver\n\nThe last missing piece is the resolver for our `user` query, to make the API returning something when querying for it.\n\nAs you may have guessed, we will create a new Python module in our `📁 resolvers` package. Let\'s call it `user.py` :\n\n``` python\nfrom turbulette import query\n\n\n@query.field("user")\nasync def user(obj, info, **kwargs):\n    return [\n        {"id": 1, "username": "Gustave Eiffel", "gender": "male", "is_staff": False},\n        {"id": 2, "username": "Marie Curie", "gender": "female", "is_staff": True},\n    ]\n\n```\n\n### 5: Run it\n\nOur `user` query is now binded to the schema, so let\'s test it.\n\nStart the server :\n\n```bash\npoetry run uvicorn app:app --port 8000\n```\n\nNow, go to [http://localhost:8000/graphql](http://localhost:8000/graphql), you will see the [GraphQL Playground](https://github.com/graphql/graphql-playground) IDE.\nFinally, run the user query, for example :\n\n``` graphql\nquery {\n  user {\n    id\n    username\n    gender\n    isStaff\n  }\n}\n```\n\nShould give you the following expected result :\n\n``` json\n{\n  "data": {\n    "user": [\n      {\n        "id": "1",\n        "username": "Gustave Eiffel",\n        "gender": "male",\n        "isStaff": false\n      },\n      {\n        "id": "2",\n        "username": "Marie Curie",\n        "gender": "female",\n        "isStaff": true\n      }\n    ]\n  }\n}\n```\n\nGood job! That was a straightforward example, showing off the bare minimum needed to set up a Turbulette API. To get the most of it, follow the User Guide.\n',
    'author': 'Matthieu MN',
    'author_email': 'matthieu.macnab@pm.me',
    'maintainer': 'Matthieu MN',
    'maintainer_email': 'matthieu.macnab@pm.me',
    'url': 'https://python-turbulette.github.io/turbulette/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
