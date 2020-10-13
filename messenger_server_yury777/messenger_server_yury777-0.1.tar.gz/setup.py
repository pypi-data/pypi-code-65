from setuptools import setup, find_packages

setup(name="messenger_server_yury777",
      version="0.1",
      description="messenger_server",
      author="Yury Kim",
      author_email="kimkrk84@mail.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
