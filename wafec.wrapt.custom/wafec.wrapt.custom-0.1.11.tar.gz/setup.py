from setuptools import setup, find_packages


setup(
    name="wafec.wrapt.custom",
    version="0.1.11",
    author="Wallace",
    author_email="wallacefcardoso@gmail.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        'wrapt>=1.12.1',
        'requests>=2.23.0'
    ]
)
