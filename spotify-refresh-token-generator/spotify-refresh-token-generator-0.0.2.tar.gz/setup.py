from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    install_requires=[
        "certifi==2020.6.20",
        "chardet==3.0.4",
        "idna==2.10; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "python-dotenv==0.14.0",
        "requests==2.24.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "six==1.15.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2'",
        "spotipy==2.16.0",
        "urllib3==1.25.10; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4' and python_version < '4'",
    ],
    name="spotify-refresh-token-generator",
    version="0.0.2",
    author="Aaron Mamparo",
    author_email="aaronmamparo@gmail.com",
    description="A command-line utility to generate a long-term refresh token for the Spotify API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amamparo/spotify-refresh-token-generator",
    package_dir={"": "src"},
    packages=find_packages("src"),
    entry_points={
        "console_scripts": [
            "generate-spotify-token = spotify_refresh_token_generator.__main__"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">= 3.7",
)
