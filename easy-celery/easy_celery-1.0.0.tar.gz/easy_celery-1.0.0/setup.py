#!/usr/bin/ python3
# -*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: kzl_knight
# Mail: 164645621@qq.com
# Created Time: 2020-10-13 00:00:00
#############################################


from setuptools import setup, find_packages

setup(
    name="easy_celery",
    version="1.0.0",
    keywords=("celery", "redis", "easy", "job"),
    description="Make multi-computer distributed tasks easier",
    long_description="Based on Redis, support task scheduling between master and slave",
    license="MIT Licence",
    url="https://github.com/kzl_knight/easy_celery",
    author="kzl_knight",
    author_email="164645621@qq.com",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        'redis>=3.5.0',
    ]
)



