""" setup.py """
import setuptools

with open("README.md") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name="torchinfo",
    version="0.0.2",
    author="Tyler Yep @tyleryep",
    author_email="tyep10@gmail.com",
    description="Pytorch model summary table containing layer sizes and shapes.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/tyleryep/torchinfo",
    packages=["torchinfo"],
    keywords=(
        "torch pytorch torchsummary torch-summary summary keras deep-learning ml "
        "torchinfo torch-info visualize model statistics layer"
    ),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
