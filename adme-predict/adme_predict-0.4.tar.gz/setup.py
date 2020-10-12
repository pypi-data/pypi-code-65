import setuptools
with open("README.md", "r") as fh:
	long_description=fh.read()
setuptools.setup(
	name="adme_predict", # Replace with your own username
	version="0.4",
	author="zhuyang",
	author_email="zhuyang0925@163.com",
	description="Our package is used for ADME attribute prediction",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/pypa/sampleproject",
	packages=setuptools.find_packages(),
	package_data={
		'':['*.pkl']
	},
	classifiers=[
	"Programming Language :: Python :: 2",
	"License :: OSI Approved :: MIT License",
	"Operating System :: OS Independent",
	],
	python_requires='>=2.6',)