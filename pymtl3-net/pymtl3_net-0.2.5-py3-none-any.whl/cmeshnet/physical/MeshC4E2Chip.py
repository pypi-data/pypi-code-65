'''
==========================================================================
MeshC4E2Chip.py
==========================================================================
A chip built with MeshC4E2Tile.

Author : Yanghui Ou
  Date : Aug 2, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL

from ..directions import *
from .MeshC4E2Tile import MeshC4E2Tile

class MeshC4E2Chip( Component ):

  def construct( s, Header, Position, ncols=2, nrows=2 ):

    # Local parameter

    s.ntiles   = ncols * nrows
    s.PhitType = mk_bits( Header.nbits )

    # Interface

    s.offchip_recv = RecvIfcRTL( s.PhitType )
    s.offchip_send = SendIfcRTL( s.PhitType )

    # Component

    s.tiles = [ MeshC4E2Tile( Header, Position ) for _ in range( s.ntiles ) ]

    # Connections

    for y in range( nrows ):
      for x in range( ncols ):
        s.tiles[ y*ncols + x ].pos //= Position( x, y )

    for i in range( s.ntiles ):
      if i // ncols > 0:
        s.tiles[i].send[SOUTH]          //= s.tiles[i-ncols].recv[NORTH]
        s.tiles[i].exp_send[SOUTH]      //= s.tiles[i-ncols].feedthru_recv[NORTH]
        s.tiles[i].feedthru_send[SOUTH] //= s.tiles[i-ncols].exp_recv[NORTH]


      if i // ncols < nrows - 1:
        s.tiles[i].send[NORTH]          //= s.tiles[i+ncols].recv[SOUTH]
        s.tiles[i].exp_send[NORTH]      //= s.tiles[i+ncols].feedthru_recv[SOUTH]
        s.tiles[i].feedthru_send[NORTH] //= s.tiles[i+ncols].exp_recv[SOUTH]

      if i % ncols > 0:
        s.tiles[i].send[WEST]          //= s.tiles[i-1].recv[EAST]
        s.tiles[i].exp_send[WEST]      //= s.tiles[i-1].feedthru_recv[EAST]
        s.tiles[i].feedthru_send[WEST] //= s.tiles[i-1].exp_recv[EAST]

      if i % ncols < ncols - 1:
        s.tiles[i].send[EAST]          //= s.tiles[i+1].recv[WEST]
        s.tiles[i].exp_send[EAST]      //= s.tiles[i+1].feedthru_recv[WEST]
        s.tiles[i].feedthru_send[EAST] //= s.tiles[i+1].exp_recv[WEST]

      if i // ncols == 0:
        s.tiles[i].send[SOUTH].rdy //= 0
        s.tiles[i].recv[SOUTH].en  //= 0
        s.tiles[i].recv[SOUTH].msg //= 0
        s.tiles[i].exp_send[SOUTH].rdy //= 0
        s.tiles[i].exp_recv[SOUTH].en  //= 0
        s.tiles[i].exp_recv[SOUTH].msg //= 0
        s.tiles[i].feedthru_send[SOUTH].rdy //= 0
        s.tiles[i].feedthru_recv[SOUTH].en  //= 0
        s.tiles[i].feedthru_recv[SOUTH].msg //= 0

      if i // ncols == nrows - 1:
        s.tiles[i].send[NORTH].rdy //= 0
        s.tiles[i].recv[NORTH].en  //= 0
        s.tiles[i].recv[NORTH].msg //= 0
        s.tiles[i].exp_send[NORTH].rdy //= 0
        s.tiles[i].exp_recv[NORTH].en  //= 0
        s.tiles[i].exp_recv[NORTH].msg //= 0
        s.tiles[i].feedthru_send[NORTH].rdy //= 0
        s.tiles[i].feedthru_recv[NORTH].en  //= 0
        s.tiles[i].feedthru_recv[NORTH].msg //= 0

      if i == 0:
        s.tiles[i].send[WEST] //= s.offchip_send
        s.tiles[i].recv[WEST] //= s.offchip_recv
        s.tiles[i].exp_send[WEST].rdy //= 0
        s.tiles[i].exp_recv[WEST].en  //= 0
        s.tiles[i].exp_recv[WEST].msg //= 0
        s.tiles[i].feedthru_send[WEST].rdy //= 0
        s.tiles[i].feedthru_recv[WEST].en  //= 0
        s.tiles[i].feedthru_recv[WEST].msg //= 0


      elif i % ncols == 0:
        s.tiles[i].send[WEST].rdy //= 0
        s.tiles[i].recv[WEST].en  //= 0
        s.tiles[i].recv[WEST].msg //= 0
        s.tiles[i].exp_send[WEST].rdy //= 0
        s.tiles[i].exp_recv[WEST].en  //= 0
        s.tiles[i].exp_recv[WEST].msg //= 0
        s.tiles[i].feedthru_send[WEST].rdy //= 0
        s.tiles[i].feedthru_recv[WEST].en  //= 0
        s.tiles[i].feedthru_recv[WEST].msg //= 0


      if i % ncols == ncols - 1:
        s.tiles[i].send[EAST].rdy //= 0
        s.tiles[i].recv[EAST].en  //= 0
        s.tiles[i].recv[EAST].msg //= 0
        s.tiles[i].exp_send[EAST].rdy //= 0
        s.tiles[i].exp_recv[EAST].en  //= 0
        s.tiles[i].exp_recv[EAST].msg //= 0
        s.tiles[i].feedthru_send[EAST].rdy //= 0
        s.tiles[i].feedthru_recv[EAST].en  //= 0
        s.tiles[i].feedthru_recv[EAST].msg //= 0

  def line_trace( s ):
    return f'{s.offchip_recv}(){s.offchip_send}'
