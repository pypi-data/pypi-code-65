import setuptools
from pathlib import Path

setuptools.setup(
     
     name ="faisalpdf",
     version = "2.3.0",
     long_description = Path("README.md").read_text(),
     packages = setuptools.find_packages(exclude=["data","test","Pipfile","Pipfile.lock"])

)