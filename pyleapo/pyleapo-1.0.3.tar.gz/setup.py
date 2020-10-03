import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="pyleapo",
	version="1.0.3",
	author="Zana Aziz",
	author_email="mail@zanaaziz.com",
	description="A Python API for accessing your Leap Card balance, overview, and travel credit history.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/zanaaziz/pyleapo",
	keywords="leap card leapcard api ireland zana",
	packages=setuptools.find_packages(),
	install_requires=[
		"Scrapy>=2.2.1",
		"scrapy-user-agents>=0.1.1"
	],
	classifiers=[
		"Programming Language :: Python :: 3.5",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	license="MIT",
	python_requires=">=3.5.2",
)
