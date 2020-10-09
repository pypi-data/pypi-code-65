# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 12:34:04 2019

@author: nelson
"""

from distutils.core import setup

setup(name='NSFopen',
      version='1.1.1',
      description='Access data and parameters from Nanosurf NID files',
      author='Edward Nelson',
      author_email='nelson@nanosurf.com',
      # package_dir = {'NSFopen':'NSFopen',
      #                'NSFopen.read':'NSFopen//read',
      #                'NSFopen.process':'NSFopen//process'},
      packages=['NSFopen','NSFopen.read','NSFopen.process']
      )
