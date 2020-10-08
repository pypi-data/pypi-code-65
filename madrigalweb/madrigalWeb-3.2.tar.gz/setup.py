"""set up file for the Python Madrigal Remote API

$Id: setup.py 7191 2020-09-08 20:18:10Z brideout $
"""
import os, os.path, sys

from distutils.core import setup
    
setup(name="madrigalWeb",
      version="3.2",
      description="Remote Madrigal Python API",
      author="Bill Rideout",
      author_email="brideout@haystack.mit.edu",
      url="http://cedar.openmadrigal.org",
      packages=["madrigalWeb"],
      keywords = ['Madrigal'],
      scripts=['madrigalWeb/globalIsprint.py', 'madrigalWeb/globalDownload.py',
               'madrigalWeb/globalCitation.py',
               'madrigalWeb/examples/exampleMadrigalWebServices.py']
      )

    