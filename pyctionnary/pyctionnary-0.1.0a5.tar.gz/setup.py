from setuptools import setup, find_packages
import os
import sys
import glob

setup(name='pyctionnary',
      description='Online pyctionnary',
      author="Theo CEVAER",
      license='GPL',
      packages=find_packages(),
      include_package_data=True,
      scripts=glob.glob('bin/**'),
      install_requires=["flask", "flask-wtf", "flask-socketio", "eventlet", "Flask-JSGlue"],
      #      data_files=[ (os.path.dirname(p) , [p] ) for p in  glob.glob('etc/**',recursive=True) if not os.path.isdir(p) ],
      zip_safe=False,
      version="0.1.0a5",
      python_requires='>=3.7'
      )
