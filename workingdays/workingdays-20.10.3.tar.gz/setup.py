import setuptools
from distutils.command.install import INSTALL_SCHEMES
from os import path

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

try:
    from workingdays._version import version as __version__
except ImportError:
    __version__ = 'unknown'

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='workingdays',
    version=__version__,
    description='A collection of Workingdays date utilities/helper functions.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Jeramie Fletcher",
    author_email="jeramie.fletcher@gmail.com",
    url="https://github.com/jeramiefletcher/workingdays",
    license="GNU General Public License v3.0",
    packages=setuptools.find_packages(),
    install_requires=['workingdays',
                      ],
    include_package_data=True,
    zip_safe=False)
