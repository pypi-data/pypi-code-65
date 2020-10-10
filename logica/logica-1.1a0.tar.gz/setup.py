import setuptools

with open("logica/README.md", "r") as f:
  long_description = f.read()

setuptools.setup(
  name = "logica",
  version = "1.1a",
  author = "Evgeny Skvortsov",
  author_email = "logica@evgeny.ninja",
  description = "Logica language.",
  long_description = long_description,
  long_description_content_type = "text/markdown",
  url="https://github.com/evgskv/logica",
  packages=setuptools.find_namespace_packages(),
  classifiers = [
      "Topic :: Database",
      "License :: OSI Approved :: Apache Software License"
  ],
  python_requires= ">=3.6"
)

