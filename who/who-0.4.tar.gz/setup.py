from setuptools import setup, find_packages


setup(
    name="who",
    version="0.4",
    author="zhongyujian PURVIS",
    author_email="tonglei@qq.com",
    description="who",
    long_description=open("README.rst").read(),
    long_description_content_type="text/markdown",
    license="Apache License, Version 2.0",
    url="",
    packages=['who'],
    package_data={'who': ['*.py']},
    install_requires=[
        ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.6"
    ],
    entry_points={

    }
)
