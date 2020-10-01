# Make sure to update the string in setup.py also (version='...')
__version__ = '1.1.0'

from chromepdf.exceptions import ChromePdfException
from chromepdf.maker import ChromePdfMaker
from chromepdf.shortcuts import generate_pdf, generate_pdf_url

__all__ = ['__version__',
           'generate_pdf', 'generate_pdf_url', 'ChromePdfException', 'ChromePdfMaker']
