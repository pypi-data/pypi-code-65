'''
==========================================================================
CMeshChip.py
==========================================================================
A chip built with CMeshTile.

Author : Yanghui Ou
  Date : Aug 2, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL

from ..directions import *
from .CMeshTile import CMeshTile

class CMeshChip( Component ):

  def construct( s, Header, Position, ncols=2, nrows=2 ):

    # Local parameter

    s.ntiles   = ncols * nrows
    s.PhitType = mk_bits( Header.nbits )

    # Interface

    s.offchip_recv = RecvIfcRTL( s.PhitType )
    s.offchip_send = SendIfcRTL( s.PhitType )

    # Component

    s.tiles = [ CMeshTile( Header, Position, ncores=4 ) for _ in range( s.ntiles ) ]

    # Connections

    for y in range( nrows ):
      for x in range( ncols ):
        s.tiles[ y*ncols + x ].pos //= Position( x, y )

    for i in range( s.ntiles ):
      if i // ncols > 0:
        s.tiles[i].send[SOUTH] //= s.tiles[i-ncols].recv[NORTH]

      if i // ncols < nrows - 1:
        s.tiles[i].send[NORTH] //= s.tiles[i+ncols].recv[SOUTH]

      if i % ncols > 0:
        s.tiles[i].send[WEST] //= s.tiles[i-1].recv[EAST]

      if i % ncols < ncols - 1:
        s.tiles[i].send[EAST] //= s.tiles[i+1].recv[WEST]

      if i // ncols == 0:
        s.tiles[i].send[SOUTH].rdy //= 0
        s.tiles[i].recv[SOUTH].en  //= 0
        s.tiles[i].recv[SOUTH].msg //= 0

      if i // ncols == nrows - 1:
        s.tiles[i].send[NORTH].rdy //= 0
        s.tiles[i].recv[NORTH].en  //= 0
        s.tiles[i].recv[NORTH].msg //= 0

      if i == 0:
        s.tiles[i].send[WEST] //= s.offchip_send
        s.tiles[i].recv[WEST] //= s.offchip_recv

      elif i % ncols == 0:
        s.tiles[i].send[WEST].rdy //= 0
        s.tiles[i].recv[WEST].en  //= 0
        s.tiles[i].recv[WEST].msg //= 0

      if i % ncols == ncols - 1:
        s.tiles[i].send[EAST].rdy //= 0
        s.tiles[i].recv[EAST].en  //= 0
        s.tiles[i].recv[EAST].msg //= 0

  def line_trace( s ):
    return f'{s.offchip_recv}(){s.offchip_send}'
