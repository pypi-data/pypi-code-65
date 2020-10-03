import os, sys

sys.path.append(os.getcwd())
sys.path.append(os.path.dirname(os.getcwd()))

from colorfultable import *

Table.limit('MAX_COLUMN_WIDTH', 10)

tb = Table((1, 2, 3, 4, 5, 6, 7, 8))
for i in range(2, 11):
    tb.addRow((i, '123456789101112'))
tb.setFoot(
    ('1.scasvas', '2.sawvbnln', '3.ahvisavagwavvgenjymmfghfrhxxzvvbsoa')
)
tb.getFoot().append('666')

tb.show(footer=True)
# tb.show(header=False)

# python3 test.py
