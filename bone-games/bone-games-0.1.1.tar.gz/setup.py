#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2020/8/29 23:01
# @Author : 詹荣瑞
# @File : setup.py
# @desc : 本代码未经授权禁止商用

from setuptools import setup, find_packages
import sys

# with open("README.md", "r", encoding='UTF-8') as fh:
#     long_description = fh.read()

setup(
    name="bone-games",
    version="0.1.1",
    keywords=["GoBang", "Game"],
    description="基于OpenCV的各种小游戏",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    license="GPL-3.0 Licence",
    # url="https://github.com/tczrr1999/PyTex",
    author="zrr",
    author_email="2742392377@qq.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    platforms="any",
    install_requires=['numpy', 'opencv-python', 'taichi'],
    scripts=[]
)

