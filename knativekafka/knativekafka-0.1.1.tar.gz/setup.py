import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="knativekafka",
    version="0.1.1",
    author="Ezhil Gowthaman",
    author_email="ezhilgowtha@gmail.com",
    description="A wrapper for kafka-python used in knative",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.optum.com/Optum-Serverless/kafka-source/tree/master/python/knativekafka",
    packages=['knativekafka'],
    python_requires='>=3.7',
    install_requires=['kafka-python'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)

