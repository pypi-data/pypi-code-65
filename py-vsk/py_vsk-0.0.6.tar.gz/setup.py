import setuptools
 
with open("README.md", "r") as fh:
  long_description = fh.read()
 
setuptools.setup(
  name = "py_vsk",
  version = "0.0.6",
  author = "WenSui Liu",
  author_email = "liuwensui@gmail.com",
  description = "Python Functions for Vasicek Distribution",
  long_description = long_description,
  long_description_content_type = "text/markdown",
  url = "https://github.com/statcompute/py_vsk",
  packages = setuptools.find_packages(),
  classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
)
