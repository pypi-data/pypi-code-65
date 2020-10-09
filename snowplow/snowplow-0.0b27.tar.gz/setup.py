import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="snowplow",
    version="0.0.b27",
    author="Patrick Stout",
    author_email="pstout@prevagroup.com",
    license="Apache2",
    description="S3 to Synapse Orchestration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ki-tools/snowplow",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=(
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts': [
            "snowplow = snowplow.cli:main"
        ]
    },
    install_requires=[
        "boto3"
    ]
)
