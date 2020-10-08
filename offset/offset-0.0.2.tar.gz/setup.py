from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='offset',
    version='0.0.2',
    author='Ron Chang',
    author_email='ron.hsien.chang@gmail.com',
    description='To encode & decode by shift text(Symmetric encryption).',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Ron-Chang/offset',
    packages=find_packages(),
    license='MIT',
    python_requires='>=3.6',
    exclude_package_date={'':['.gitignore', 'img', 'dev', 'test', 'setup.py']},
    scripts=['bin/offset'],
    install_requires=[]
)
