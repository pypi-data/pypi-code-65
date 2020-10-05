from setuptools import setup, find_packages

from ru_proverbs import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

CLASSIFIERS = [
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8"
]

setup(
    name='ru_proverbs',
    version=__version__,
    license='MIT',
    description='RU Proverbs generator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Yurii Serhiichuk',
    author_email='savik.ne@gmail.com',
    url='https://github.com/xSAVIKx/ru-proverbs',
    keywords=['python', 'textgenrnn', 'ML', 'AI', 'tensorflow'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'tensorflow>=2.3.1',
        'textgenrnn>=2.0.0',
        'pip>=20.2.3'
    ],
    scripts=['bin/ru-proverbs', 'bin/ru-proverbs.py'],
    classifiers=CLASSIFIERS,
    python_requires='>=3.7'
)
