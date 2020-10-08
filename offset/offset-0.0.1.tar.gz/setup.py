from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='offset',
    version='0.0.1',
    author='Ron Chang',
    author_email='ron.hsien.chang@gmail.com',
    description='To encode & decode by shift text.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Ron-Chang/offset',
    packages=find_packages(),
    scripts=['bin/offset'],
    license='MIT',
    python_requires='>=3.6',
    exclude_package_date={'':['GUI', '.gitignore', 'dev', 'test', 'setup.py']},
    install_requires=[
    ]
)
