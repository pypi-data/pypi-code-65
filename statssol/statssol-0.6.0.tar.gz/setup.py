import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='statssol',  
     version='0.6.0',
     py_modules=['statssol'] ,
     author="**insert Author**",
     author_email="some_email@mail.ru",
     description="stats",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://some_website.nice",
     install_requires=['PyTelegramBotApi', 'cloudinary', 'requests'],
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
