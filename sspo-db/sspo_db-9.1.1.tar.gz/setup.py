from setuptools import setup, find_packages
setup(
    name='sspo_db',  # Required
    version="9.1.1",  # Required
    author="Paulo Sergio dos Santo Junior",
    author_email="paulossjuniort@gmail.com",
    description="A lib to access SSPO DB",
 
    packages=find_packages(),
    
    install_requires=[
        'SQLAlchemy', 'SQLAlchemy-Utils', 'factory-boy', 'SQLAlchemy-serializer'
    ],

    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
    setup_requires=['wheel'],
    
)
