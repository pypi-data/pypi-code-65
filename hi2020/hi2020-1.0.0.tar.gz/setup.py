#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
@File  : setup.py
@Author: HappyLay
@Date  : 2020/10/15 13:32
@Desc  : 安徽理工大学
"""
__author__ = 'HappyLay'

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hi2020",  # 模块名称
    version="1.0.0",  # 当前版本
    author="happylay",  # 作者
    # author_email="",  # 作者邮箱
    description="一个hi问候包",  # 模块介绍
    long_description=long_description,  # 模块详细介绍
    long_description_content_type="text/markdown",  # 模块详细介绍格式
    # url="",  # 模块github地址
    packages=setuptools.find_packages(),  # 自动找到项目中导入的模块

    # 模块相关的元数据（更多描述信息）
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    # 依赖模块
    install_requires=[
        'pillow',
    ],
    python_requires='>=3'
)
