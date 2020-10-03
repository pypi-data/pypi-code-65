from pathlib import Path

from setuptools import find_packages
from setuptools import setup

setup(
    name="LDB_Inventory_Barcode",
    packages=['ldb', 'ldb.inventory', 'ldb.inventory.barcode'],
    namespace_packages=['ldb', 'ldb.inventory'],
    url="https://www.eldebe.org/ldb/inventory/barcode/",
    license="LICENSE",
    author="Alex Orange",
    author_email="alex@eldebe.org",
    description=(
        "Create standard barcodes with Python. No external modules needed. "
        "(optional Pillow support included)."
    ),
    long_description=Path("README.rst").read_text(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={"console_scripts":
                  ["python-barcode = ldb.inventory.barcode.pybarcode:main"]},
    use_scm_version={
        "version_scheme": "post-release",
        "write_to": "ldb/inventory/barcode/version.py",
    },
    setup_requires=["setuptools_scm"],
    extras_require={"images": ["pillow"],
                    "pdf": ["reportlab"],
                   },
    tests_require=["pytest"],
    include_package_data=True,
)
