from setuptools import setup, find_packages

setup(name="mess_server_prj",
      version="0.0.3",
      description="mess_server_prj",
      author="Ivan Ivanov",
      author_email="iv.iv@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
