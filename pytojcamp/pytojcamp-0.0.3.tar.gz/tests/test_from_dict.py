# -*- coding: utf-8 -*-
"""Test the ntuple conversion"""
from pytojcamp.from_dict import from_dict


def test_from_dict(make_data_dictionary):
    """Test the conversion based on a data dict"""
    jcamp_string = from_dict(make_data_dictionary)
    expected_string = """##TITLE=
##JCAMP-DX=6.00
##DATA TYPE=
##ORIGIN=
##OWNER=
##NTUPLES= 
##VAR_NAME=  x,y,z
##SYMBOL=    x,y,z
##VAR_TYPE=  INDEPENDENT,DEPENDENT,DEPENDENT
##VAR_DIM=   3,3,3
##UNITS=     cm,h,kg
##PAGE= N=1
##DATA TABLE= (x,y,z..x,y,z), PEAKS
1\t2\t3
3\t2\t3
3\t2\t3
##END"""
    assert jcamp_string == expected_string
