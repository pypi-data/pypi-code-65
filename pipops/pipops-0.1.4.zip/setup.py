"""Setup script for pieops"""

from setuptools import setup, find_packages
import os

version = '0.1.4'


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def reqs(*f):
    return list(filter(None, [strip_comments(l) for l in open(
        os.path.join(os.getcwd(), *f)).readlines()]))


with open('README.md') as readme_file:
    README = readme_file.read()

setup(name='pipops',
      version=version,
      description="PipOps is an AiOps inspired project created and self managed by Vishal Raj (DevOps Specialist)",
      long_description=README,
      long_description_content_type='text/markdown',
      author='Vishal Raj',
      author_email='iiamvishalraj@gmail.com',
      url='https://github.com/iiamvishalraj',
      packages=find_packages(),
      license='Apache 2.0',
      include_package_data=True,
      zip_safe=False,
      install_requires=reqs('requirements.txt'),
      scripts=['pipops/__init__.py'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.8',
      ],
      )
