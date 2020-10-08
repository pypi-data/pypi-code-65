import setuptools

setuptools.setup(
    name='compound_split',
    version='1.0.2.dev1',
    install_requires=[],
    python_requires='>=3',
    author="Don Tuggener",
    author_email="don.tuggener@gmail.com",
    maintainer="Joel Niklaus",
    maintainer_email="me@joelniklaus.ch",
    description="Splits a compound into its body and head. So far German and Dutch are supported.",
    license='GPL-3.0 License',
    long_description=open('README.md', "r").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JoelNiklaus/CompoundSplit",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ]
)
