'''
==========================================================================
MeshC4E2Tile_test.py
==========================================================================
Some simple tests for the MeshC4E2Tile.

Author : Yanghui Ou
  Date : Aug 12, 2020
'''
import pytest
from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from ocnlib.rtl.queues import NormalQueueRTL as Queue

from ..MeshC4E2Tile import MeshC4E2Tile

@bitstruct
class Packet32:
  dst_x   : Bits4
  dst_y   : Bits4
  dst_ter : Bits3
  plen    : Bits4
  filler  : Bits17

@bitstruct
class Packet64:
  src_x  : Bits4
  src_y  : Bits4
  dst_x  : Bits4
  dst_y  : Bits4
  dst_ter: Bits3
  plen   : Bits4
  filler : Bits41

@bitstruct
class Packet128:
  src_x   : Bits4
  src_y   : Bits4
  dst_x   : Bits4
  dst_y   : Bits4
  dst_ter : Bits3
  plen    : Bits4
  filler  : Bits105

@bitstruct
class Packet256:
  src_x   : Bits4
  src_y   : Bits4
  dst_x   : Bits4
  dst_y   : Bits4
  dst_ter : Bits3
  plen    : Bits4
  filler  : Bits233

@bitstruct
class Packet512:
  src_x   : Bits4
  src_y   : Bits4
  dst_x   : Bits4
  dst_y   : Bits4
  dst_ter : Bits3
  plen    : Bits4
  filler  : mk_bits(489)

@bitstruct
class Position:
  pos_x : Bits4
  pos_y : Bits4

pkt_dict = {
  32  : Packet32,
  64  : Packet64,
  128 : Packet128,
  256 : Packet256,
  512 : Packet512,
}

@pytest.mark.parametrize(
  'nbits, channel_lat', [
  ( 32,  0 ),
  ( 32,  1 ),
  ( 64,  0 ),
  ( 64,  1 ),
  ( 128, 0 ),
  ( 128, 1 ),
  ( 256, 0 ),
  ( 256, 1 ),
  ( 512, 0 ),
  ( 512, 1 ),
  ( 32,  0 ),
  ( 32,  1 ),
  ( 64,  1 ),
  ( 128, 1 ),
  ( 256, 1 ),
  ( 512, 1 ),
])
def test_translate( nbits, channel_lat ):
  Pkt = pkt_dict[ nbits ]
  assert Pkt.nbits == nbits

  if channel_lat % 2 == 0:
    send_lat = channel_lat // 2
    recv_lat = channel_lat // 2

  else:
    send_lat = channel_lat // 2 + 1
    recv_lat = channel_lat // 2

  # if channel_lat % 2 == 0:
  #   north_lat = channel_lat
  #   east_lat  = channel_lat
  #   south_lat = channel_lat
  #   west_lat  = channel_lat

  dut = MeshC4E2Tile( Pkt, Position )

  dut.set_param( 'top.router.input_units*.construct', QueueType=Queue )
  dut.set_param( 'top.channels*.construct', QueueType=Queue, latency=[send_lat, recv_lat] )
  dut.set_param( 'top.exp_channels*.construct', QueueType=Queue, latency=[send_lat, recv_lat] )


  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'MeshC4E2Tile_{nbits}b{channel_lat}q' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()
