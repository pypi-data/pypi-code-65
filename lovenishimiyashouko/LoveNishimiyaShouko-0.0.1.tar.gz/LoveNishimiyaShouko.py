import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LoveNishimiyaShouko",
    version="0.0.1",
    author="LoveNishimiyaShouko",
    author_email="LoveNishimiyaShouko@LoveNishimiyaShouko.LoveNishimiyaShouko",
    description="Auto check in.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LoveNishimiyaShouko/LoveNishimiyaShouko",
    license="AGPLv3",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords="auto,check in,auto check in",
    project_urls={
        "Documentation": "https://github.com/LoveNishimiyaShouko/LoveNishimiyaShouko/tree/main/docs",
        "Source": "https://github.com/LoveNishimiyaShouko/LoveNishimiyaShouko/tree/main/code"
    },
    packages=setuptools.find_packages(include=['LoveNishimiyaShouko']),
    install_requires=["requests"],
    python_requires='>=3',
    package_data={
        'LoveNishimiyaShouko_log': ['LoveNishimiyaShouko_log.txt'],
        'LoveNishimiyaShouko_error': ['LoveNishimiyaShouko_error.txt']
    },
    entry_points={
        'console_scripts': [
            'checkin=LoveNishimiyaShouko:main',
        ],
    },
)
