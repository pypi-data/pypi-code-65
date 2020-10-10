import setuptools



setuptools.setup(
    name="Fsearch",
    packages=setuptools.find_packages(),
    version="0.0.10",
    license='MIT',
    author="Sacha",
    author_email="",
    description="GoogleSearch",
    long_description_content_type="text/markdown",
    url="https://github.com/SachaGitHub/GoogleSearch",
    download_url='https://github.com/SachaGitHub/GoogleSearch',
    keywords=['GoogleSearch'],
    install_requires=[
        'requests',
        "bs4"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
    ],
    include_package_data=True
)
