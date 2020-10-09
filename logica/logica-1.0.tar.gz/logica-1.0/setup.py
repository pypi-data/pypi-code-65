import setuptools

long_description = "Logica programming lanugage."

setuptools.setup(
  name = "logica",
  version = "1.0",
  author = "Evgeny Skvortsov",
  author_email = "logica@evgeny.ninja",
  description = "Logica language.",
  long_description_content_type = "text/markdown",
  url="https://github.com/evgskv/logica",
  packages=setuptools.find_packages(),
  classifiers = [
      "Topic :: Database"
  ],
  python_requires= ">=3.6"
)

