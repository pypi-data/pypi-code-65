import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TwilioToEmail",
    version="0.0.7",
    author="Ruckshan Ratnam",
    author_email="hendryratnam@gmail.com",
    description="A middle man service that acts as a Twilio wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lowmoney/twilio_to_email",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests'],
    python_requires='>=3.6',
)