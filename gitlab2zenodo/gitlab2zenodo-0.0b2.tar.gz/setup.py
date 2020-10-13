from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='gitlab2zenodo',
    license='Apache License Version 2.0',
    version='0.0.b2',
    packages=find_packages(),
    url='https://gitlab.com/sbeniamine/gitlab2zenodo',
    author='Sacha Beniamine',
    install_requires=['requests', 'responses'],
    entry_points = {
        "console_scripts": [
            "g2z-send = gitlab2zenodo.main:g2z_command",
            "g2z-get-meta = gitlab2zenodo.main:g2z_meta_command",
        ]
    },
    description='Sends gitlab snapshots to zenodo Automatically.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.5',
    keywords='zenodo gitlab',
    classifiers=["Development Status :: 4 - Beta",
                 "Intended Audience :: Developers",
                 "Intended Audience :: Science/Research",
                 "License :: OSI Approved :: Apache Software License",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python :: 3",
                 "Programming Language :: Python :: 3.5",
                 "Programming Language :: Python :: 3.6",
                 "Programming Language :: Python :: 3.7",
                 ]
)
