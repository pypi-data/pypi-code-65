#!/usr/bin/python
# coding: utf-8

# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ccad import ReactorCAD as rea
from ccad import FilterReactorCAD as f_rea
from ccad import FloatingFilterReactorCAD as ff_rea
from ccad import SiphonCAD as siph
from ccad import DoubleSiphonCAD as d_siph
from ccad import TubeConnectorCAD as t_con
from ccad import Assembly

ass = Assembly(automatic_angles=True)
# ass = Assembly()

# First module, filter reactor
r_1 = rea(70, rea.T_CUSTOM, rea.B_ROUND_IN_O)

r_1.addLuerTopInlet("i1")
r_1.addLuerTopInlet("i2")
r_1.autoPlaceTopInlets()
ass.appendModule(r_1)

# Second module, filter reactor
r_2 = ff_rea(66, 14, rea.T_CLOSED_ROUND_O, rea.B_FLAT, 37.4, 1.8)
r_2.addInputPercentageBottom("entry", height_per=95)
r_2.addOutputPercentageTop("exit", height_per=10, angle=0)
r_2.addInputPercentageBottom("manual", height_per=95, angle=-90, external=True)
ass.appendModule(r_2)

# First connector, from 1st to 2nd module
con1 = d_siph(r_1, r_1.outputs["default"], r_2, r_2.inputs["entry"])

ass.appendModule(con1)

r_3 = rea(60, rea.T_CLOSED_ROUND_O, rea.B_ROUND)
r_3.addInputPercentage("entry", height_per=100)
r_3.align_top_strategy = 'lift'

ass.appendModule(r_3)

con2 = t_con(r_2, r_2.outputs["exit"], r_3, r_3.inputs["entry"])

ass.appendModule(con2)

ass.addAlignTops(r_1, r_2)
ass.addAlignTops(r_3, r_2)

ass.refresh()

ass.fn = 75

ass.saveProject("jasmine.ccad")

ass.renderToFile("jasmine.scad")

if __name__ == "__main__":
    pass
