#encoding=utf-8
from distutils.core import setup

setup(
    name="baizhanAsa",#对外模块名称
    version='1.0',#版本
    description='这是第一个对外发布的模块，测试哦',#描述
    author='Asa',
    author_email='heiyijiushi@163.com',
    py_modules=['baizhanAsa.demo1'] #要发布的模块
)

#1.构建发布文件：python setup.py sdist
#2.安装本地模块 python setpu.py install 文件安装在lib/site-packages目录中
#3.导入模块 import baizhanMath2.demo1
