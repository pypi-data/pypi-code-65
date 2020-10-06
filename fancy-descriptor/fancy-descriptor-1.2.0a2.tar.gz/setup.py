from pathlib import Path

from setuptools import setup, find_namespace_packages

package_dir = Path("./fancy/descriptor")
readme_file = package_dir / "README.md"

with readme_file.open() as fp:
    long_description = fp.read()


setup(
    name="fancy-descriptor",
    version="1.2.0.a2",
    packages=find_namespace_packages(),
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.md", "*.txt"],
    },

    # metadata to display on PyPI
    author="su-rin",
    author_email="susautw@gmail.com",
    description="This package add a callable descriptor called method descriptor which can apply on methods.",
    keywords="descriptor",
    project_urls={
        "Source Code": "https://github.com/susautw/fancy_descriptors",
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
