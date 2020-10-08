'''
==========================================================================
TorusChip.py
==========================================================================
A chip built with TorusTile.

Author : Yanghui Ou
  Date : Aug 2, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from ocnlib.ifcs.CreditIfc import CreditRecvIfcRTL, CreditSendIfcRTL

from ..directions import *
from .TorusTile import TorusTile

class TorusChip( Component ):

  def construct( s, Header, Position, ncols=2, nrows=2 ):

    # Local parameter

    s.ntiles   = ncols * nrows
    s.PhitType = mk_bits( Header.nbits )

    # Interface

    s.offchip_recv = CreditRecvIfcRTL( s.PhitType, vc=2 )
    s.offchip_send = CreditSendIfcRTL( s.PhitType, vc=2 )

    s.offchip_feedthru_recv = CreditRecvIfcRTL( s.PhitType, vc=2 )
    s.offchip_feedthru_send = CreditSendIfcRTL( s.PhitType, vc=2 )

    # Component

    s.tiles = [ TorusTile( Header, Position ) for _ in range( s.ntiles ) ]

    # Connections

    for y in range( nrows ):
      for x in range( ncols ):
        # FIXME: position assignment is wrong because the torus is folded!
        s.tiles[ y*ncols + x ].pos //= Position( x, y )

    for i in range( s.ntiles ):
      if i // ncols > 0:
        s.tiles[i].send[SOUTH]          //= s.tiles[i-ncols].feedthru_recv[NORTH]
        s.tiles[i].feedthru_send[SOUTH] //= s.tiles[i-ncols].recv[NORTH]

      if i // ncols < nrows - 1:
        s.tiles[i].send[NORTH]          //= s.tiles[i+ncols].feedthru_recv[SOUTH]
        s.tiles[i].feedthru_send[NORTH] //= s.tiles[i+ncols].recv[SOUTH]

      if i % ncols > 0:
        s.tiles[i].send[WEST]          //= s.tiles[i-1].feedthru_recv[EAST]
        s.tiles[i].feedthru_send[WEST] //= s.tiles[i-1].recv[EAST]

      if i % ncols < ncols - 1:
        s.tiles[i].send[EAST]          //= s.tiles[i+1].feedthru_recv[WEST]
        s.tiles[i].feedthru_send[EAST] //= s.tiles[i+1].recv[WEST]

      if i // ncols == 0:
        s.tiles[i].send[SOUTH] //= s.tiles[i].feedthru_recv[SOUTH]
        s.tiles[i].recv[SOUTH] //= s.tiles[i].feedthru_send[SOUTH]

      if i // ncols == nrows - 1:
        s.tiles[i].send[NORTH] //= s.tiles[i].feedthru_recv[NORTH]
        s.tiles[i].recv[NORTH] //= s.tiles[i].feedthru_send[NORTH]

      if i == 0:
        s.tiles[i].send[WEST] //= s.offchip_send
        s.tiles[i].recv[WEST] //= s.offchip_recv
        s.tiles[i].feedthru_send[WEST] //= s.offchip_feedthru_send
        s.tiles[i].feedthru_recv[WEST] //= s.offchip_feedthru_recv

      elif i % ncols == 0:
        s.tiles[i].send[WEST] //= s.tiles[i].feedthru_recv[WEST]
        s.tiles[i].recv[WEST] //= s.tiles[i].feedthru_send[WEST]

      if i % ncols == ncols - 1:
        s.tiles[i].send[EAST] //= s.tiles[i].feedthru_recv[EAST]
        s.tiles[i].recv[EAST] //= s.tiles[i].feedthru_send[EAST]


  def line_trace( s ):
    return f'{s.offchip_recv}(){s.offchip_send}'
