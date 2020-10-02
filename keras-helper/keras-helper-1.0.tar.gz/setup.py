"""
keras-helper: helpful keras wrapper
"""
from setuptools import setup, find_packages

VERSION = '1.0'

def get_requirements():
    with open('requirements.txt') as requirements:
        for req in requirements:
            req = req.strip()
            if req and not req.startswith('#'):
                yield req


def get_readme():
    with open('README.md') as readme:
            return readme.read()

setup(name='keras-helper',
      version=VERSION,
      description="Helpful Keras Import Wrapper",
      long_description=get_readme(),
      long_description_content_type='text/markdown',
      classifiers=['Topic :: Software Development :: Libraries :: Python Modules'],
      keywords='keras mxnet cntk plaidml tensorflow theano cuda numpy numpy-intel pandas ray modin scikit-learn matplotlib seaborn plotly helper ai ml datascience',
      author='Karthik Kumar Viswanathan',
      author_email='karthikkumar@gmail.com',
      url='https://github.com/guilt/keras-helper',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'examples.*', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=list(get_requirements()),
     )