import setuptools
import re

with open("README.md") as f:
    long_description = f.read()

with open("uonet_request_signer_hebe/__init__.py") as f:
    text = f.read()
    __name__ = re.search(r"__name__ = \"(.*?)\"", text)[1]
    __version__ = re.search(r"__version__ = \"(.*?)\"", text)[1]

setuptools.setup(
    name=__name__,
    version=__version__,
    description="UONET+ (hebe) request signer for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wulkanowy/uonet-request-signer",
    author="Wulkanowy",
    author_email="wulkanowyinc@gmail.com",
    maintainer="Kuba Szczodrzyński",
    maintainer_email="kuba@szczodrzynski.pl",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Topic :: Education",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=setuptools.find_packages(),
    install_requires=["pyopenssl"],
    extras_require={"testing": ["pytest"]},
)
