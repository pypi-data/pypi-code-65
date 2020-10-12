import setuptools
from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()
try:
    with open("requirements.txt", "r") as req:
        install_requires = [item.strip() for item in req.readlines()]
except FileNotFoundError:
    with open("marshmallow_advanced.egg-info/requires.txt", "r") as req:
        install_requires = [item.strip() for item in req.readlines()]


setup(name='marshmallow_advanced',
      version='1.1.2',
      url='https://github.com/maximshumilo/tools',
      long_description=long_description,
      description='Lib marshmallow advanced',
      packages=setuptools.find_packages(),
      author='Shumilo Maksim',
      author_email='shumilo.mk@gmail.com',
      install_requires=install_requires,
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Programming Language :: Python :: 3.8",
          "Intended Audience :: Developers",
          'Topic :: Software Development',
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires='>=3.8',
      zip_safe=False)

