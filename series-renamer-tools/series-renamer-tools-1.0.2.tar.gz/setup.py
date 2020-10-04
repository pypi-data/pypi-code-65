import os.path

from setuptools import find_packages, setup

setup(
    name='series-renamer-tools',
    description='Series Renamer: rename files of series with respect to episode number.',
    long_description=open(os.path.join(
        os.path.dirname(__file__), 'README.md')).read(),
    long_description_content_type='text/markdown',
    version='1.0.2',
    packages=find_packages(),
    install_requires=["natsort==7.0.1"],
    url='https://github.com/seehait/series-renamer-tools',
    entry_points={
        'console_scripts': ['series-renamer=src.main:main'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Utilities',
    ],
    license='MIT'
)
