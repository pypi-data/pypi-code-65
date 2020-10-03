from setuptools import setup

VERSION = open("VERSION", "r").read()

setup(
    name='tf_complex_channels',
    packages=['tf_complex_channels'],
    version=VERSION,
    description='A library to work with complex number deep learning.',
    long_description=open("README.md", "r").read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    url='https://github.com/lukewood/tf-complex-channels',
    author='Luke Wood',
    author_email='lukewoodcs@gmail.com',
    license='MIT',
)
