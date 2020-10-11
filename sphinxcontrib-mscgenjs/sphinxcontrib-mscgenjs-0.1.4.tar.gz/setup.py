# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

long_desc = '''
This package contains the mscgenjs_ Sphinx_ extension.

.. _mscgenjs: https://mscgen.js.org/
.. _Sphinx: http://sphinx.pocoo.org/

Allow mscgen-formatted Message Sequence Chart (MSC) graphs to be included in
Sphinx-generated documents inline. For example::

    .. mscgenjs::
    
        msc {
            hscale = "0.5";
    
            a,b,c;
    
            a->b [ label = "ab()" ] ;
            b->c [ label = "bc(TRUE)"];
            c=>c [ label = "process()" ];
        }
'''

requires = ['Sphinx>=0.6']

setup(
    name='sphinxcontrib-mscgenjs',
    version='0.1.4',
    url='https://github.com/LoveIsGrief/sphinxcontrib-mscgenjs',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-mscgenjs',
    license='BOLA',
    author='LoveIsGrief',
    author_email='loveisgrief@tuta.io',
    description='mscgenjs Sphinx extension',
    long_description=long_desc,
    zip_safe=False,
    project_urls={
        "Bugs": "https://github.com/LoveIsGrief/sphinxcontrib-mscgenjs/issues"
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
