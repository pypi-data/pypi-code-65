import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='fashioner',  
     version='v0.0.1-alpha',
     scripts=[] ,
     author="Ceyda Cinarel",
     author_email="snu_ceyda@gmail.com",
     description="placeholder until made opensource",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/cceyda/fasioNER",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
    python_requires='>=3.6',
    install_requires=["pyyaml","coloredlogs"]
 )