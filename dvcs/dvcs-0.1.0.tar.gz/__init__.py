# coding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

_package_data = dict(
    full_package_name='dvcs',
    version_info=(0, 1, 0),
    __version__='0.1.0',
    author='Anthon van der Neut',
    author_email='a.van.der.neut@ruamel.eu',
    description='manipulate bazaar, fossil, git, mercurial repositories',
    keywords='pypi statistics',
    entry_points='dvcs=dvcs.__main__:main',
    # entry_points=None,
    license='Copyright Ruamel bvba 2007-2020',
    since=2020,
    # status="α|β|stable",  # the package status on PyPI
    # data_files="",
    universal=True,
    install_requires=['ruamel.appconfig', 'ruamel.std.argparse>=0.8', 'argcomplete'],
        # py27=["ruamel.ordereddict"],
    tox=dict(
        env='23',  # *->all p->pypy
    ),
)


version_info = _package_data['version_info']
__version__ = _package_data['__version__']
