#encoding=utf-8
from distutils.core import  setup
setup(
    name="mwbTest",#对外模块的名字,要跟你创建的文件夹的名字一致，不然你都不知道怎么调用
    version='1.0',#版本号
    description="孟维彬的第一个python发布",#描述
    author='mwb',#作者
    author_email='mwb@mwb.com',#作者邮箱
    py_modules=["mwbTest.demo"]#要发布的模块
)