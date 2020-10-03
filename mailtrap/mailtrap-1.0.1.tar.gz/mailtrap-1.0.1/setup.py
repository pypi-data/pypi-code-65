import os
import subprocess
import shutil

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

with open('README.md') as f:
    readme = f.read()

setup(
    name='mailtrap',
    version='1.0.1',
    description='MailTrap has been renamed to Sendria. Use Sendria now! An SMTP server that makes all received mails accessible via a web interface and REST API.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/msztolcman/mailtrap',
    project_urls={
        'GitHub: Sendria issues': 'https://github.com/msztolcman/sendria/issues',
        'GitHub: Sendria repo': 'https://github.com/msztolcman/sendria',
    },
    download_url='https://github.com/msztolcman/sendria',
    author='Marcin Sztolcman',
    author_email='marcin@urzenia.net',
    license='MIT',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'mailtrap = mailtrap.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Communications :: Email',
        'Topic :: Software Development',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
        'Framework :: AsyncIO',
    ]
)
