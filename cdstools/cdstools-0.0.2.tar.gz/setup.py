from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Financial and Insurance Industry',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='cdstools',
    version='0.0.2',
    description='Tools designed for use with CDS data',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='https://github.com/732jhy',
    author='Justin Yu',
    author_email='732jhy@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='Credit Default Swap',
    packages=find_packages(),
    install_requires=['numpy','scipy']
)



