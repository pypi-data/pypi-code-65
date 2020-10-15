# coding=utf-8
from pathlib import Path
from setuptools import setup, find_packages


def read_by_lines(path, encoding="utf-8"):
    result = list()
    with open(path, "r", encoding=encoding) as infile:
        result = [line for line in infile]
    return result


filepath = './requirements.txt'
require_pkgs = read_by_lines(filepath)
data_files = [filepath]

setup(
    name='fx_nb_log',  #
    version="3.4.8",
    description=(
        'modified nb_log'
    ),
    keywords=("logging", "logger", "multiprocess file handler", "color handler"),
    long_description_content_type="text/markdown",
    long_description=open('README.md', 'r', encoding='utf8').read(),
    data_files=data_files,
    author='ydf',
    author_email='ydf0509@sohu.com',
    maintainer='fx',
    maintainer_email='fengxin@826.com',
    license='BSD License',
    packages=find_packages(),
    include_package_data=True,
    platforms=["all"],
    url='https://gitee.com/toosimple-tools/nb_log',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=require_pkgs
)
"""
#打包上传

## 直接使用python命令
python setup.py sdist upload -r pypi

## 使用twine
pip install -U twine
python setup.py sdist
twine upload dist/fx_nb_log-3.4.8.tar.gz 
twine upload dist/*

#即时安装，不用等待 阿里云 豆瓣 同步
pip install fx_nb_log -U -i https://pypi.org/simple
"""
