import os

import setuptools

from version import __version__

CURRENT_FILEPATH = os.path.abspath(os.path.dirname(__file__))
VERSION_FILENAME = 'version.py'


setuptools.setup(
    name="bbc-dslib",
    version=__version__,
    author="Raphaël Berly",
    author_email="raphael.berly@blablacar.com",
    description="A lib for the Data Science team at Blablacar",
    license='closed',
    url="https://bitbucket.corp.blablacar.com/projects/lib/repos/dslib",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=['humanfriendly', 'pyyaml', 'jinja2'],
    extras_require={
        'google': [
            'google-cloud-bigquery>=1.18.0,<2.0.0dev',  # pandas-gbq 0.13.3 blocks us below 2.0.0dev
            'google-cloud-bigquery-storage==0.8.0',  # otherwise missing beta class for now
            'google-api-python-client', 'pyarrow',
            'oauth2client', 'grpcio', 'pandas', 'pandas-gbq', 'tqdm', 'google-cloud-storage',
            'gspread==3.6.0', 'gspread-dataframe==3.0.6'
        ],
        'prophet': ['fbprophet'],
        'database': ['sqlalchemy', 'psycopg2-binary', 'PyMySQL', 'pandas'],
    }
)
