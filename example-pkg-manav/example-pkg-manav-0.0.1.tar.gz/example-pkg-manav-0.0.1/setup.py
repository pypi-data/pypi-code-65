import setuptools
with open("README.md","r") as fh:
	long_description=fh.read()

setuptools.setup(
	name="example-pkg-manav",
	version='0.0.1',
	author="Example Author",
	description="A small Example Package",
	long_description=long_description,
	long_description_content_type="text/markdown",
	packages=setuptools.find_packages(),
	classifier=[
		"Programming Language :: Python :: 3",
		"Operating System :: OS Independent",
	],
	python_requied=">=3.6"
)
