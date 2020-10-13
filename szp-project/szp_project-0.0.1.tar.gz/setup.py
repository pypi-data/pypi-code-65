import setuptools
import os
# 切换到当前文件所在的目录
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "szp_project",
    version="0.0.1",
    author="szp",
    author_email="zhengpushi@126.com",
    description="Just a test",
    long_description = long_description,
    long_description_content_type="text/markdown",
    url = "http://www.fem-nuaa.cn",
    py_modules = ['langspeak',],
    packages = setuptools.find_packages(),
    classifiers = ("Programming Language :: Python :: 3",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   ),
)
