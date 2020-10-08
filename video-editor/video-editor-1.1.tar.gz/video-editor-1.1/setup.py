import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='video-editor',    # This is the name of your PyPI-package.
    version='1.1',          # Update the version number for new releases
    author="Snehangshu Karmakar",
    author_email="snehangshu@gmail.com",
    decription="Video editing tool using ffmpeg",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/snehangshuk/video-editor",
    packages=setuptools.find_packages(),
    install_requires=[
          'PyYAML',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    scripts=['video-editor/video-cut']
)
