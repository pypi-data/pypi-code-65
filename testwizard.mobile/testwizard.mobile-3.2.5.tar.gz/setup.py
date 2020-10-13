import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="testwizard.mobile",
    version="3.2.5",
    author="Eurofins Digital Testing - Belgium",
    author_email="support-be@eurofins.com",
    description="Testwizard for Mobile testobjects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['testwizard.mobile'],
    install_requires=[
        'testwizard.test==3.2.5',
        'testwizard.testobjects-core==3.2.5',
        'testwizard.commands-audio==3.2.5',
        'testwizard.commands-mobile==3.2.5',
        'testwizard.commands-video==3.2.5'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.3",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
    ],
)
