"""
=========================================================================
MeshC4E2RouteUnitRTL.py
=========================================================================
A DOR-Y route unit with get/give interface for CMesh.

Author : Yanghui Ou
  Date : Aug 20, 2020
"""
from pymtl3 import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL

from .directions import *


class MeshC4E2RouteUnitRTL( Component ):

  def construct( s, PacketType, PositionType ):

    # Constants

    s.num_outports = 12
    TType = mk_bits( clog2(num_outports) )

    # Interface

    s.get  = GetIfcRTL( PacketType )
    s.give = [ GiveIfcRTL (PacketType) for _ in range ( s.num_outports ) ]
    s.pos  = InPort( PositionType )

    # Componets

    s.give_ens = Wire( mk_bits( s.num_outports ) )
    s.give_rdy = [ Wire() for _ in range( s.num_outports )]

    # Connections

    for i in range( s.num_outports ):
      s.get.ret     //= s.give[i].ret
      s.give_ens[i] //= s.give[i].en
      s.give_rdy[i] //= s.give[i].rdy

    # Routing logic

    @update
    def up_ru_routing():

      for i in range( s.num_outports ):
        s.give_rdy[i] @= 0

      if s.get.rdy:
        if (s.pos.pos_x == s.get.ret.dst_x) & (s.pos.pos_y == s.get.ret.dst_y):
          s.give_rdy[8+zext(s.get.ret.dst_ter,TType)] @= 1

        # South
        elif s.get.ret.dst_y < s.pos.pos_y:
          if s.pos.pos_y - s.get.ret.dst_y >= 2:
            s.give_rdy[5] @= 1
          else:
            s.give_rdy[1] @= 1

        # North
        elif s.get.ret.dst_y > s.pos.pos_y:
          if s.get.ret.dst_y - s.pos.pos_y >= 2:
            s.give_rdy[4] @= 1
          else:
            s.give_rdy[0] @= 1

        # West
        elif s.get.ret.dst_x < s.pos.pos_x:
          if  s.pos.pos_x - s.get.ret.dst_x >= 2:
            s.give_rdy[6] @= 1
          else:
            s.give_rdy[2] @= 1

        # East
        else:
          if s.get.ret.dst_x - s.pos.pos_x >= 2:
            s.give_rdy[7] @= 1
          else:
            s.give_rdy[3] @= 1

    @update
    def up_ru_get_en():
      s.get.en @= s.give_ens > 0

  # Line trace

  def line_trace( s ):
    out_str = "|".join([ f"{s.give[i]}" for i in range( s.num_outports ) ])
    return f"{s.get}(){out_str}"
