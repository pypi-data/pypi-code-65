import os
import setuptools

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), 'r') as fh:
    long_description = fh.read()


setuptools.setup(
    name='sycfgr',
    version='0.0.3',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Christoph Hartmann',
    author_email='mail_to_chriss@posteo.net',
    url='https://github.com/chriss-de/sycfgr',
    py_modules=['sycfgr'],
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'PyYAML>=5.3.0,<6',
    ],
)
