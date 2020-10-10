import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Django-CryptographicFields", # Replace with your own username
    version="1.2.0",
    author="Shahprogrammer",
    author_email="dhwanil38@gmail.com",
    description="A Django app for cryptography in Django Models.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Shahprogrammer/Django-CryptographicFields",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django :: 3.1",
        "Topic :: Security :: Cryptography",
        
    ],
    install_requires=[
          'django>=3.1.1','pycryptodome>=3.9.8'
      ],
  python_requires='>=3.6'
    )
