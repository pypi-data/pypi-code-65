""" Setup module """
import setuptools
import incubus

setuptools.setup(
    name="incubus-keremkoseoglu",
    version=incubus.__version__,
    author=incubus.AUTHOR,
    author_email=incubus.EMAIL,
    description=incubus.DESCRIPTION,
    long_description=incubus.DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/keremkoseoglu/incubus",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=incubus.PYTHON_VERSION,
    install_requires=[],
    include_package_data=True
)