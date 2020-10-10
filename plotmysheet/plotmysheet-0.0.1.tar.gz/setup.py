from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='plotmysheet',
    version='0.0.1',
    description='This package will plot a graph between the two columns of your choice from google sheet.',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Suraj Patidar',
    author_email='surjpatidar9999@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='plotspreadsheet',
    packages=find_packages(),
    install_requires=['matplotlib','gspread','oauth2client','importjson']
)