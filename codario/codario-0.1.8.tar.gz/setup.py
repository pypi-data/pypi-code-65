
from setuptools import setup, find_packages
from codario.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='codario',
    version=VERSION,
    description='Codario is a cloud-based service that helps you to stay secure with your open source dependencies.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Alexey Beloglazov',
    author_email='alexey.beloglazov@codario.io',
    url='https://codario.io',
    license='Apache License 2.0',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'codario': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        codario = codario.main:main
    """,
    install_requires=['cement', 'pyyaml', 'colorlog', 'jinja2', 'urllib3', 'tinydb', 'tabulate']
)
