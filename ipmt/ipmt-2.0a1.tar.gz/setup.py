# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ipmt']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=2.10.1,<3.0.0',
 'Mako>=1.0.7,<2.0.0',
 'PyYAML>=5.3.1,<6.0.0',
 'docker>=4.3.1,<5.0.0',
 'psycopg2>=2.7.7,<3.0.0']

entry_points = \
{'console_scripts': ['ipmt = ipmt.cli:main']}

setup_kwargs = {
    'name': 'ipmt',
    'version': '2.0a1',
    'description': 'Schema migration tools for PostgreSQL',
    'long_description': 'IPMT\n====\n\n.. image:: https://img.shields.io/pypi/v/ipmt.svg\n    :target: https://pypi.python.org/pypi/ipmt\n\n.. image:: https://img.shields.io/travis/inplat/ipmt.svg\n    :target: https://travis-ci.org/inplat/ipmt\n\n.. image:: https://codecov.io/gh/inplat/ipmt/branch/master/graph/badge.svg\n    :target: https://codecov.io/gh/inplat/ipmt\n\n.. image:: https://readthedocs.org/projects/ipmt/badge/?version=latest\n    :target: http://ipmt.readthedocs.io/ru/latest/?badge=latest\n    :alt: Documentation Status\n\n.. image:: https://pyup.io/repos/github/inplat/ipmt/shield.svg\n    :target: https://pyup.io/repos/github/inplat/ipmt/\n    :alt: Updates\n\n.. image:: https://landscape.io/github/inplat/ipmt/master/landscape.svg?style=flat\n   :target: https://landscape.io/github/inplat/ipmt/master\n   :alt: Code Health\n\nИструмент миграций СУБД PostgreSQL\n\n\nВозможноти\n----------\n* Версионирование схемы БД\n* Ветвление в версиях\n* Управление привилегиями с помощью yaml файлов\n\n\nДокументация\n-------------\nhttp://ipmt.readthedocs.io/ru/latest/\n\n\nУстановка\n---------\nДля установки выполните в консоли::\n\n    $ pip install ipmt\n\n\nИспользование\n-------------\n\nВыполните в консоли::\n\n    # инициализация репозитория\n    ipmt init\n    # создание первой версии\n    ipmt create baseline\n    # отредактируйте файл миграции разместив SQL в\n    # первом аргументе db.execute функции up для\n    # наката миграции и в аналогичном месте функции\n    # down для отката миграции\n    vim versions/000001#baseline.py\n    # накат версии на указанную БД\n    IPMT_DSN=username@hostname/dbname ipmt up\n',
    'author': 'InPlat',
    'author_email': 'dev@inplat.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/inplat/ipmt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
