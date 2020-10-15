from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.8'
]

setup(
    name='iapa',
    packages=['iapa'],
    version='0.1',
    description='Predictive Analytics Library',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Sng Hao Jun',
    author_email='snghaojun@outlook.sg',
    license='MIT',
    classifiers=classifiers,
    keywords='predict',
    install_requires=['numpy','scikit-learn','pandas']
)