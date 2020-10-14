from setuptools import setup, find_packages

setup(name="databases_and_PyQt_server",
      version="0.0.2",
      description="databases_and_PyQt_server_app",
	  long_description="Final version of server_app from GeekBrains course Databases and PyQt",
	  long_description_content_type="text/markdown",
      author="Yriy Batiouk",
      author_email="bagumg@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
