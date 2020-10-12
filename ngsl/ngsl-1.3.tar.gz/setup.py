from setuptools import setup, find_packages

setup(
    name="ngsl",
    version='1.3',
    description='You can check if the word is in New General Service List',
    author='Kobori Akira',
    author_email='private.beats@gmail.com',
    url='https://github.com/koboriakira/ngsl',
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
