#! /usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

setuptools.setup(
    name='vsatcloud',  # 包的名字
    author='vsattech.com',  # 作者
    version='0.1.7',  # 版本号
    description='vsat-cloud python sdk',  # 描述
    long_description="",
    long_description_content_type="text/markdown",
    author_email='it@vsattech.com',  # 你的邮箱**
    url='https://vsat.cloud',  # 可以写github上的地址，或者其他地址
    packages=setuptools.find_packages(),

    # 依赖包
    install_requires=['requests >= 2.19.1'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    zip_safe=True,
)
