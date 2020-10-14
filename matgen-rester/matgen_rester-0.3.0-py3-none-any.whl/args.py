# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 10:20:44 2020

@author: LENOVO
"""

import argparse
def parse_cml_args(cml):
	parser = argparse.ArgumentParser(description="manual to this script")
	parser.add_argument("-e", "--elements",dest='e', action='store',help="find the structures that contain the specific elements",type=str,default = None)
	parser.add_argument("-ne", "--nelements",dest='ne', action='store',help="find the structures that do not contain the specific elements",type=str,default = None)
	parser.add_argument("-id", "--matid",dest='id', action='store',help="find structures that have the same matid",type=str,default = None)
	parser.add_argument("-p", dest='p', action='store',type=int,default = 0)
	parser.add_argument("-s", dest='s', action='store',type=int,default = 0)
	parser.add_argument("-cs","--crystalSystem", dest='cs', action='store',type=str)
	parser.add_argument("-sg","--spaceGroup", dest='sg', action='store',type=str)
	parser.add_argument("-v", "--volume",dest='v', action='store',type=str)
	parser.add_argument("-f", dest='f', action='store',type=str,default = None)
	parser.add_argument("-o", dest='o', action='store',type=str,default = None)
	return parser.parse_args(cml)
# arg = argparse.ArgumentParser(description="manual to this script")
# arg.add_argument('--kmesh', dest='kmesh', action='store', type=int,
#                      default=None, nargs=3,
#                      help='the kmesh in the KPOINTS')

# args = arg.parse_args()
# print(args.new_kmesh,type(args.new_kmesh))
