from setuptools import setup, find_packages

import os
import sys


PYTHON3 = sys.version_info > (3, )
HERE = os.path.abspath(os.path.dirname(__file__))


def readme():
    with open(os.path.join(HERE, 'README.md')) as f:
        return f.read()


def get_version():
    with open(os.path.join(HERE, 'svc_tracer/__init__.py'), 'r') as f:
        content = ''.join(f.readlines())
    env = {}
    if PYTHON3:
        exec(content, env, env)
    else:
        compiled = compile(content, 'get_version', 'single')
        eval(compiled, env, env)
    return env['__version__']


setup(
  name='svc-tracer',
  version=get_version(),
  description='Service tracer base on scapy',
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
  keywords='pcap service thrift tracer',
  url='https://github.com/gebing/svc-tracer',
  license='Apache License 2.0',
  author='gebing',
  author_email='gebing@foxmail.com',
  packages=find_packages(),
  scripts=['svc-tracer'],
  include_package_data=True,
  platforms = "any",
  install_requires=[
    'six',
    'ply',
    'ptsd',
    'scapy',
    'thrift',
    'pprintpp',
  ],
)
