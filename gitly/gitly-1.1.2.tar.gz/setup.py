import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='gitly',
    packages=setuptools.find_packages(),
    description='This is a lib to help you plot your fency graphs from plotly in github while using Google Colab notebook.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version='1.1.2',
    url='https://github.com/Tiagoeem/gitly',
    author='Tiago Sanches da Silva',
    author_email='tiago.eem@gmail.com',
    license='mit',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        'plotly>=4.9.0',
        'kaleido'
    ]
    )