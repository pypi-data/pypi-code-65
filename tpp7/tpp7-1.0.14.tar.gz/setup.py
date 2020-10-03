import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="tpp7", # Replace with your own username
	version="1.0.14",
	author="Olivier Cardoso",
	author_email="Olivier.Cardoso@univ-paris-diderot.fr",
	description="Un paquetage pour les TP de Physique de l'université Paris-Diderot",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/cardosoo/tp",
	package_dir={'': 'src'},
	packages=setuptools.find_packages(where='src'),
	scripts=['tests/Osc.py', 'tests/minimalTPUsage.py'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	install_requires=[
		'numpy', 'scipy', 'matplotlib', 'python-usbtmc', 'pandas', 'pyusb'
	],
	python_requires='>=3.6',
)
