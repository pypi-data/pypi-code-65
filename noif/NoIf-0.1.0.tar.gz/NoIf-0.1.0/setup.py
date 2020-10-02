# coding=utf-8

from setuptools import setup, find_packages


setup(
    name='NoIf',

    version="0.1.0",
    description=(
        'A chinese chat bot'
    ),
    long_description='No more if else code',
    long_description_content_type="text/markdown",
    author='Jansen Leo',
    author_email='2835347017@qq.com',
    maintainer='Jansen Leo',
    maintainer_email='2835347017@qq.com',
    license='MIT License',
    packages=find_packages(),
    platforms=["linux", 'windows'],
    url='https://github.com/AngelovLee/NoIf',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
    ]
)