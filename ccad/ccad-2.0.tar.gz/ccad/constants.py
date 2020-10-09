#!/usr/bin/python
# coding: utf-8

"""
Define 'enumerations' here.

Used to define top and bottom types, for modules
"""

# The walls of any part should be 3 mm thick to be leakproof
WALLS = 3

# Thickness of walls when a filter has to be inserted
WALLS_F = 4

# Thickness of walls for support circle under reactors
WALLS_S = 2

# Bottom walls, minimum thickness if external inlet
WALL_BOT_MIN = 3

# Threaded top, walls must be at least WALL_THREAD_MIN thick
WALL_THREAD_MIN = 3

# A filter space has a diameter of: d_filter + OFF_FILTER
# Allows insertion of the filter when printing
OFF_FILTER = 0.85

# Filter is merged of SECURE_D_FILTER mm in the walls, on both sides
SECURE_D_FILTER = 2

# At least SECURE_H_FILTER must be printed on top of a filter
# 0.9 = 3 * 0.3mm layers
SECURE_H_FILTER_TOP = 0.9

# Canula's diameter
D_CAN = 3

# Diameter of the hole for external inlet
D_EXT_INLET = 5

# Length of external inlet
L_EXT_INLET = 7

# Add extra length to bottom external adaptor, to make sure they can be
# taped properly
ADD_TAP_BOTTOM = 3

# Height of top with thread
H_THREADED_TOP = 15

# Radii for threaded tops
R_2_QUA_INCH = 10
R_3_QUA_INCH = 12
R_4_QUA_INCH = 16

# Define the golden ratio, used to calculate dimensions of reactors
PHI = (1 + 5 ** 0.5) / 2

# 3µm length to avoid non manifold surfaces (OpenSCAD bug)
F = 0.003
