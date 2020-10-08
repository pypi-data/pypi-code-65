'''
==========================================================================
CMeshTile.py
==========================================================================
'''
from pymtl3 import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from pymtl3.stdlib.basic_rtl import Reg

from ocnlib.rtl.DummyCore import DummyCore as DummyCore
from channel.BidirectionalChannelRTL import BidirectionalChannelRTL as Channel

from ..CMeshRouterRTL import CMeshRouterRTL
from ..directions import *

class CMeshTile( Component ):

  def construct( s, PacketType, PositionType, ncores=4 ):

    # Local parameter

    num_inports  = 4 + ncores
    num_outports = 4 + ncores
    PhitType     = mk_bits( PacketType.nbits )

    # Interface

    s.recv = [ RecvIfcRTL( PhitType ) for _ in range(4) ]
    s.send = [ SendIfcRTL( PhitType ) for _ in range(4) ]
    s.pos  = InPort( PositionType )

    # Components

    s.cores  = [ DummyCore( PhitType ) for _ in range(ncores) ]
    s.router = CMeshRouterRTL( PacketType, PositionType,
                               num_inports, num_outports )
    s.channels = [ Channel( PacketType ) for _ in range(4) ]

    # s.channel_n = [ Channel( PacketType, latency=north_lat ) for _ in range(2) ]
    # s.channel_s = [ Channel( PacketType, latency=south_lat ) for _ in range(2) ]
    # s.channel_w = [ Channel( PacketType, latency=west_lat ) for _ in range(2) ]
    # s.channel_e = [ Channel( PacketType, latency=east_lat ) for _ in range(2) ]

    # s.channel_n = Channel( PacketType, latency=north_lat )
    # s.channel_s = Channel( PacketType, latency=south_lat )
    # s.channel_w = Channel( PacketType, latency=west_lat )
    # s.channel_e = Channel( PacketType, latency=east_lat )

    s.pos_reg = Reg( PositionType )

    # Connections

    s.pos //= s.pos_reg.in_
    s.pos_reg.out //= s.router.pos

    @update
    def up_cmesh_tiles():
      for i in range(ncores):
        s.cores[i].recv.msg    @= s.router.send[i+4].msg
        s.cores[i].recv.en     @= s.router.send[i+4].en
        s.router.send[i+4].rdy @= s.cores[i].recv.rdy

        s.router.recv[i+4].msg @= s.cores[i].send.msg
        s.router.recv[i+4].en  @= s.cores[i].send.en
        s.cores[i].send.rdy    @= s.router.recv[i+4].rdy

      for i in range(4):
        s.channels[i].recv[0].msg @= s.router.send[i].msg
        s.channels[i].recv[0].en  @= s.router.send[i].en
        s.router.send[i].rdy      @= s.channels[i].recv[0].rdy

        s.send[i].msg             @= s.channels[i].send[0].msg
        s.send[i].en              @= s.channels[i].send[0].en
        s.channels[i].send[0].rdy @= s.send[i].rdy

        s.router.recv[i].msg      @= s.channels[i].send[1].msg
        s.router.recv[i].en       @= s.channels[i].send[1].en
        s.channels[i].send[1].rdy @= s.router.recv[i].rdy

        s.channels[i].recv[1].msg @= s.recv[i].msg
        s.channels[i].recv[1].en  @= s.recv[i].en
        s.recv[i].rdy             @= s.channels[i].recv[1].rdy

      # North

      # s.channel_n[0].recv.msg  @= s.router.send[NORTH].msg
      # s.channel_n[0].recv.en   @= s.router.send[NORTH].en
      # s.router.send[NORTH].rdy @= s.channel_n[0].recv.rdy

      # s.send[NORTH].msg       @= s.channel_n[0].send.msg
      # s.send[NORTH].en        @= s.channel_n[0].send.en
      # s.channel_n[0].send.rdy @= s.send[NORTH].rdy

      # s.router.recv[NORTH].msg @= s.channel_n[1].send.msg
      # s.router.recv[NORTH].en  @= s.channel_n[1].send.en
      # s.channel_n[1].send.rdy  @= s.router.recv[NORTH].rdy

      # s.channel_n[1].recv.msg @= s.recv[NORTH].msg
      # s.channel_n[1].recv.en  @= s.recv[NORTH].en
      # s.recv[NORTH].rdy       @= s.channel_n[1].recv.rdy

      # # South

      # s.channel_s[0].recv.msg  @= s.router.send[SOUTH].msg
      # s.channel_s[0].recv.en   @= s.router.send[SOUTH].en
      # s.router.send[SOUTH].rdy @= s.channel_s[0].recv.rdy

      # s.send[SOUTH].msg       @= s.channel_s[0].send.msg
      # s.send[SOUTH].en        @= s.channel_s[0].send.en
      # s.channel_s[0].send.rdy @= s.send[SOUTH].rdy

      # s.router.recv[SOUTH].msg @= s.channel_s[1].send.msg
      # s.router.recv[SOUTH].en  @= s.channel_s[1].send.en
      # s.channel_s[1].send.rdy  @= s.router.recv[SOUTH].rdy

      # s.channel_s[1].recv.msg @= s.recv[SOUTH].msg
      # s.channel_s[1].recv.en  @= s.recv[SOUTH].en
      # s.recv[SOUTH].rdy       @= s.channel_s[1].recv.rdy


      # # West

      # s.channel_w[0].recv.msg @= s.router.send[WEST].msg
      # s.channel_w[0].recv.en  @= s.router.send[WEST].en
      # s.router.send[WEST].rdy @= s.channel_w[0].recv.rdy

      # s.send[WEST].msg        @= s.channel_w[0].send.msg
      # s.send[WEST].en         @= s.channel_w[0].send.en
      # s.channel_w[0].send.rdy @= s.send[WEST].rdy

      # s.router.recv[WEST].msg @= s.channel_w[1].send.msg
      # s.router.recv[WEST].en  @= s.channel_w[1].send.en
      # s.channel_w[1].send.rdy @= s.router.recv[WEST].rdy

      # s.channel_w[1].recv.msg @= s.recv[WEST].msg
      # s.channel_w[1].recv.en  @= s.recv[WEST].en
      # s.recv[WEST].rdy        @= s.channel_w[1].recv.rdy


      # # East

      # s.channel_e[0].recv.msg @= s.router.send[EAST].msg
      # s.channel_e[0].recv.en  @= s.router.send[EAST].en
      # s.router.send[EAST].rdy @= s.channel_e[0].recv.rdy

      # s.send[EAST].msg        @= s.channel_e[0].send.msg
      # s.send[EAST].en         @= s.channel_e[0].send.en
      # s.channel_e[0].send.rdy @= s.send[EAST].rdy

      # s.router.recv[EAST].msg @= s.channel_e[1].send.msg
      # s.router.recv[EAST].en  @= s.channel_e[1].send.en
      # s.channel_e[1].send.rdy @= s.router.recv[EAST].rdy

      # s.channel_e[1].recv.msg @= s.recv[EAST].msg
      # s.channel_e[1].recv.en  @= s.recv[EAST].en
      # s.recv[EAST].rdy        @= s.channel_e[1].recv.rdy


    # for i in range(ncores):
    #   s.cores[i].recv    //= s.router.send[i+4]
    #   s.router.recv[i+4] //= s.cores[i].send


    # for i in range(4):
    #   s.channels[i].recv[0] //= s.router.send[i]
    #   s.send[i]             //= s.channels[i].send[0]

    #   s.router.recv[i] //= s.channels[i].send[1]
    #   s.channels[i].recv[1] //= s.recv[i]

  def line_trace( s ):
    return s.router.line_trace()
