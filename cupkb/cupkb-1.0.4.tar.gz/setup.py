from setuptools import find_packages,setup


setup(name='cupkb',version='1.0.4',description="text2sql",
      #packages=["ckpt","conceptNet","data","preprocess","saved_model","src"],
      packages=find_packages(),
      py_modules=["train"],
      data_files=["well_data_1.xls"],
      install_requires=['record','torch==1.6.0','matplotlib'])