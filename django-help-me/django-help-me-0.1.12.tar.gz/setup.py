# --------------------------------------------
# Copyright 2015-2020, Grant Viklund
# @Author: Grant Viklund
# --------------------------------------------

from os import path
from setuptools import setup, find_packages

from helpme.__version__ import VERSION

readme_file = path.join(path.dirname(path.abspath(__file__)), 'README.md')

try:
    from m2r import parse_from_file
    long_description = parse_from_file(readme_file)     # Convert the file to RST for PyPI
except ImportError:
    # m2r may not be installed in user environment
    with open(readme_file) as f:
        long_description = f.read()


package_metadata = {
    'name': 'django-help-me',
    'version': VERSION,
    'description': 'An app for providing a simple Help Desk & FAQ for users.',
    'long_description': long_description,
    'url': 'https://github.com/renderbox/django-help-me/',
    'author': 'Grant Viklund, Mackenzie Camisa',
    'author_email': 'renderbox@example.com',
    'license': 'MIT license',
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    'keywords': ['django', 'app'],
}

setup(
    **package_metadata,
    packages=find_packages(),
    package_data={'helpme': ['templates/helpme/*.html', 'static/js/support/*.js']},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        'Django>=3.1, <3.2',
        'django-autoslug',
        'django-multiselectfield',
        'django-crispy-forms',
        'django-user-agents',
    ],
    extras_require={
        'dev': [
            'django-extensions',
            'django-allauth',
            'dj-database-url',
            'psycopg2-binary',
            'pylint',
            'djangorestframework',
            'pyyaml',
            'ua-parser',
            'user-agents',
        ],
        'test': [],
        'prod': [],
        'build': [
            'setuptools',
            'wheel',
            'twine',
            'm2r',
        ],
        'docs': [
            'coverage',
            'Sphinx',
            'sphinx-rtd-theme',
            'recommonmark',
            'rstcheck',
        ],
    }
)
