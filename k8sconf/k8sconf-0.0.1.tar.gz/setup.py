import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="k8sconf",
    version="0.0.1",
    author="M. Miedema",
    author_email="git@number42.net",
    description="Apply configuration through env or mounted secrets in Kubernetes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/number42net/k8sconf",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta"
    ],
    python_requires='>=3.6',
)
