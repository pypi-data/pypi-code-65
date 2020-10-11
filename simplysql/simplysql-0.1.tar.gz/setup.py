from distutils.core import setup

setup(name="simplysql",
      packages=["simplysql"],
      version="0.1",
      license="MIT",
      description="Simplified editing of SQL databases (sqlite3) without having to deal with queries!",
      author="Pit Nahrstedt",
      author_email="luanee@web.de",
      url="https://github.com/Luanee/SimplySQL",
      download_url="https://github.com/Luanee/SimplySQL/archive/v0.1.0.tar.gz",
      keywords=["sql", "easy", "queries", "databases", "sqlite3"],
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Developers",
                   "Topic :: Software Development :: Build Tools",
                   "License :: OSI Approved :: MIT License",
                   # TODO: Check compatibility
                   # "Programming Language :: Python :: 3",
                   # "Programming Language :: Python :: 3.4",
                   # "Programming Language :: Python :: 3.5",
                   "Programming Language :: Python :: 3.7"],
      )
