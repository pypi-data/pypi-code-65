'''
    PyVantagePro2
    ------------

    Communication tools for the Davis VantagePro2 devices.


'''
import re
import sys
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

README = open(os.path.join(here, 'README.md')).read()

REQUIREMENTS = [
    'pylink',
    'progressbar-latest',
]

if sys.version_info < (2, 7):
    REQUIREMENTS.append('ordereddict')

if sys.version_info < (2, 7) or (3,) <= sys.version_info < (3, 2):
    # In the stdlib from 2.7:
    REQUIREMENTS.append('argparse')


with open(os.path.join(os.path.dirname(__file__), 'pyvantagepro2',
                        '__init__.py')) as init_py:
    release = re.search("VERSION = '([^']+)'", init_py.read()).group(1)
# The short X.Y version.
version = release.rstrip('dev')

setup(
    name='PyVantagePro2',
    version=version,
    url='',
    license='GNU GPL v3',
    description='Communication tools for the Davis VantagePro2 devices',
    author='',
    author_email='',
    maintainer='',
    maintainer_email='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: Internet',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=find_packages(),
    zip_safe=False,
    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'pyvantagepro = pyvantagepro.__main__:main'
        ],
    },
)
