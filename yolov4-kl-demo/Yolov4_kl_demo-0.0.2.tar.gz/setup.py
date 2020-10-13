import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Yolov4_kl_demo",
    version="0.0.2",
    author="cleverhans",
    author_email="xx@xx.com",
    description="Yolov4 with kl loss integrated",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=["torch==1.6.0",
                      "matplotlib",
                      "opencv-python",
                      "easydict"],
)