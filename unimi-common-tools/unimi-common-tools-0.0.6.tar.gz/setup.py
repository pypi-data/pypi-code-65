import setuptools


try:
    # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:
    # for pip <= 9.0.3
    from pip.req import parse_requirements


def load_requirements(fname):
    reqs = parse_requirements(fname, session="test")
    requirements = [str(ir.requirement) for ir in reqs]
    return requirements


def long_description(fname):
    with open(fname) as f:
        return f.read()


setuptools.setup(
    name='unimi-common-tools',
    version='0.0.6',
    scripts=[],
    author="Binay Kumar Ray",
    author_email="binayray2009@gmail.com",
    description="UniMI Common Tools",
    long_description=long_description('README.md'),
    long_description_content_type="text/markdown",
    url="https://github.com/binayr/UniMI-common-tools",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=load_requirements('requirements.txt'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
