import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="autocheckin",
    version="0.0.2",
    author="LoveNishimiyaShouko",
    author_email="LoveNishimiyaShouko@LoveNishimiyaShouko.LoveNishimiyaShouko",
    description="Auto check in.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LoveNishimiyaShouko/autocheckin",
    license="AGPLv3",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ],
    keywords="auto,check in,auto check in",
    project_urls={
        "Documentation": "https://github.com/LoveNishimiyaShouko/autocheckin/docs",
        "Source": "https://github.com/LoveNishimiyaShouko/autocheckin"
    },
    packages=setuptools.find_packages(include=['autocheckin']),
    install_requires=["requests"],
    python_requires='>=3',
    package_data={
        'autocheckin_log': ['autocheckin_log.txt'],
        'autocheckin_error': ['autocheckin_error.txt']
    },
    entry_points={
        'console_scripts': [
            'checkin=autocheckin:main',
        ],
    },
)
