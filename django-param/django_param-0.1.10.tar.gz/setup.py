from setuptools import setup, find_namespace_packages
from os import path

# -- Python Dependencies -- #
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django_param',
    version='0.1.10',
    description='Django Param provides the ParamForm class which translates a param class into a native Django Form.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='',
    author='htran',
    author_email='htran@aquaveo.com',
    url='https://github.com/tethysplatform/django_param',
    license='BSD 2-Clause License',
    packages=find_namespace_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    test_suite='tests'
)
