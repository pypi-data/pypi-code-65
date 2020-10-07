import re

from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('hyperfoil/__init__.py', 'rt', encoding='utf8') as f:
    VERSION = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

requirements = ['requests', 'pyyaml']

extra_requirements = {
    'dev': [
        'pytest',
        'python-dotenv'
    ],
    'docs': ['sphinx']
}

setup(name='hyperfoil-client',
      version=VERSION,
      description='Hyperfoil python client',
      author='Jakub Smadis',
      author_email='jakub.smadis@gmail.com',
      maintainer='Jakub Smadis',
      url='https://github.com/jsmadis/hyperfoil-python-client',
      packages=find_packages(exclude=('tests',)),
      long_description=long_description,
      long_description_content_type='text/markdown',
      include_package_data=True,
      install_requires=requirements,
      extras_require=extra_requirements,
      entry_points={},
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Topic :: Utilities',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: Apache Software License',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.8',
      ],
      )
