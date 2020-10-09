import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = fh.readlines()


setuptools.setup(
    name="wasu_test",
    version="1.9.2",
    author="XiaoDong Chen",
    author_email="chenxiaodong@wasu.com",
    description="The Wasu Auto TestFrameWork",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    # install_requires=['PyYAML>=5.3', 'PyMySql>=0.10.1',
    #                   'xlrd>=1.2.0', 'requests==2.24.0',
    #                   'selenium==3.141.0', 'python-benedict==0.19.0', 'Appium-Python-Client~=1.0.2',
    #                   ],
    install_requires=install_requires,
    entry_points={

    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
