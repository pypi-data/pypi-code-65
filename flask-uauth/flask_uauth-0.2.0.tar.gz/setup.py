from setuptools import setup, find_packages


def get_long_description():
    with open("README.md", "r") as f:
        return f.read()


setup(
    name="flask_uauth",
    version="0.2.0",
    author="Panagiotis Matigakis",
    author_email="pmatigakis@gmail.com",
    description="Simple authentication for Flask REST apis",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/pmatigakis/flask-uauth",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "Flask>=1.0"
    ],
    tests_require=["nose"],
    test_suite="nose.collector",
    zip_safe=True,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)
