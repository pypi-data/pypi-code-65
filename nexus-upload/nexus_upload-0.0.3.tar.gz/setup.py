from setuptools import setup, find_packages

import os
import sys


PYTHON3 = sys.version_info > (3, )
HERE = os.path.abspath(os.path.dirname(__file__))


def readme():
    with open(os.path.join(HERE, 'README.md')) as f:
        return f.read()


def get_version():
    with open(os.path.join(HERE, 'nexus_upload/__init__.py'), 'r') as f:
        content = ''.join(f.readlines())
    env = {}
    if PYTHON3:
        exec(content, env, env)
    else:
        compiled = compile(content, 'get_version', 'single')
        eval(compiled, env, env)
    return env['__version__']


setup(
  name='nexus_upload',
  version=get_version(),
  description='Upload packages to Nexus server',
  long_description=readme(),
  long_description_content_type='text/markdown',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: System :: Distributed Computing',
    'Topic :: System :: Networking',
  ],
  keywords='nexus package upload',
  url='https://github.com/gebing/nexus_upload',
  license='Apache License 2.0',
  author='gebing',
  author_email='gebing@foxmail.com',
  packages=find_packages(),
  scripts=['nexus-upload'],
  include_package_data=True,
  platforms = "any",
  install_requires=[
    "requests",
    "paramiko",
  ],
)
