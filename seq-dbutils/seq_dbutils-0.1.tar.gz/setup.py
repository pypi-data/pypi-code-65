from setuptools import setup

setup(name="seq_dbutils",
      version="0.1",
      author="Laura Thomson",
      author_email="laura.thomson@bdi.ox.ac.uk",
      description="A package of MySQL database utilities",
      packages=["seq_dbutils"],
      install_requires=["cryptography",
                        "pandas",
                        "SQLAlchemy",
                        "mysql-connector-python"],
      license="MIT",
      python_requires='>=3.6',
      url="https://github.com/BDI-pathogens/seq_dbutils",
      )
