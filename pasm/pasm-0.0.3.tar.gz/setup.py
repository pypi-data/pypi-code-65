import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name="pasm", # Replace with your own username
    version="0.0.3",
    author="Pranay Manocha",
    author_email="pranaymnch@gmail.com",
    description="A pip package for perceptual audio metric",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pranaymanocha/PerceptualAudio",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
