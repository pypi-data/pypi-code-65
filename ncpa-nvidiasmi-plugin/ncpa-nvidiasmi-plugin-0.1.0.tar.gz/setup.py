#!/usr/bin/env python

from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='ncpa-nvidiasmi-plugin',
        python_requires='>3.5.2',
        version="0.1.0",
        author='Matt Cockayne',
        author_email='matt@phpboyscout.uk',
        license="MIT",
        zip_safe=True,
        packages=find_packages('src'),
        package_dir={'': 'src'},
        keywords="nagios ncpa nvidia smi gpu plugin",
        url='https://github.com/phpboyscout/ncpa-nvidiasmi-plugin',
        description='NCPA plugin to check status of Nvidia GPUs using nvidia-smi',
        long_description=readme(),
        long_description_content_type="text/markdown",
        install_requires=[
            "argparse",
            "nagiosplugin"],
        scripts=["src/check_nvidiasmi.py"],

)
