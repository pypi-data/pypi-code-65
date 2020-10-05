#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation
# All rights reserved.
#-------------------------------------------------------------------------

import os

NOTICE = os.path.join(os.path.abspath(__file__), '..', '..', 'NOTICE.rst')
with open(NOTICE, 'r', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup_cfg = dict(
    name='winui',
    version='0.1',
    description='This package name is reserved by Microsoft Corporation',
    long_description=LONG_DESCRIPTION,
    author='Microsoft Corporation',
    author_email='python@microsoft.com',
    url='https://aka.ms/python',
    packages=[],
)

from distutils.core import setup
setup(**setup_cfg)
