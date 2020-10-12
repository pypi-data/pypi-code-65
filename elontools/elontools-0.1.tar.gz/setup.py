#encoding=utf-8
from setuptools import setup, find_packages

setup(
    name="elontools",
    version="0.1",
    packages=find_packages(),
    install_requires=['pyexiv2'],
    description="Elon's Tools",
    long_description="elontool",
    author="Elon",
    author_email="oneplus@126.com",

    license="GPL",
    keywords=("oneplus"),
    platforms="Independant",
    url="https://gitee.com/ElonWu/piptool",
    entry_points= {
        'console_scripts': [
            'oneplus = image_backup.oneplus:run',
            ],
    }

)