#!/usr/bin/env python
# -*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: iRabbit
# Mail: 8381595@qq.com
# Created Time:  2020.10.10
#############################################

from setuptools import setup, find_packages  # 这个包没有的可以pip一下

setup(
    name='irabbitpro',
    version='1.0.0',
    description='a automated test tools',
    author='irabbit',
    author_email='8381595@qq.com',
    url='https://github.com/irabbit666/RabbitHttp',
    packages=find_packages(),
    install_requires=['requests'],
)
