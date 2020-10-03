import setuptools

with open("README.md", 'r') as fh:
      long_description = fh.read()

setuptools.setup(
      name="mllb",
      version="0.0.3",
      author="Iyobosa Evbayowieru",
      author_email="theiyobosa@outlook.com",
      description="Machine Learning package",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/theiyobosa/mllb",
      packages=setuptools.find_packages(),
      classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
    ],
      python_requires='>=3.6',
)