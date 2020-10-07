# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os; os.chdir("S:/siat")
from siat.bond import *

aytm=0.08
yper=3
fv=100
c=0.1
mterm=1
bond_malkiel4(aytm,yper,c,fv,mterm)

bplist=[-300,-250,-200,-150,-100,-50,50,100,150,200,250,300]
bplist=[-50,-40,-30,-20,-10,10,20,30,40,50]
bplist=[-250,-200,-150,-100,-50,50,100,150,200,250]
bplist=[-500,-400,-300,-200,-100,100,200,300,400,500]
bond_malkiel4(aytm,yper,c,fv,mterm,bplist)

