from setuptools import setup, find_packages

setup(name="databases_and_PyQt_client",
      version="0.0.1",
      description="databases_and_PyQt_client_app",
	  long_description="Final version of client_app from GeekBrains course Databases and PyQt",
	  long_description_content_type="text/markdown",
      author="Yriy Batiouk",
      author_email="bagumg@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
