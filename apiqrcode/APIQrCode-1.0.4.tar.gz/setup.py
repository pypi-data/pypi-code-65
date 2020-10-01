# -*- coding: utf-8 -*-

import os

from setuptools import setup

README = os.path.join(os.path.dirname(__file__), 'README.md')

setup(
    name='APIQrCode',
    version='1.0.4',
    description='SDK API QrCode Python Cielo',
    author='Júnior Carvalho',
    author_email='joseadolfojr@gmail.com',
    url='https://github.com/Jeitto/sdk-qrcode-cielo.git',
    keywords='cielo qrcode',
    install_requires=['requests', 'pycrypto'],
    license='MIT',
    packages=['APIQrCode'],
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    )
)
