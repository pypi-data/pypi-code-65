from setuptools import setup, find_packages

setup(name="databases_and_PyQt_server",
      version="0.0.1",
      description="databases_and_PyQt_server_app",
      author="Yriy Batiouk",
      author_email="bagumg@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
