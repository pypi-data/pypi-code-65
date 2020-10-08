'''
==========================================================================
CMeshTile_test.py
==========================================================================
Some simple tests for the CMeshTile.

Author : Yanghui Ou
  Date : Aug 12, 2020
'''
import pytest
from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from ocnlib.rtl.queues import NormalQueueRTL as Queue

from ..CMeshTile import CMeshTile

@bitstruct
class Packet32:
  dst_x   : Bits8
  dst_y   : Bits8
  dst_ter : Bits3
  plen    : Bits4
  filler  : Bits9

@bitstruct
class Packet64:
  src_x  : Bits8
  src_y  : Bits8
  dst_x  : Bits8
  dst_y  : Bits8
  dst_ter: Bits3
  plen   : Bits4
  filler : Bits25

@bitstruct
class Packet128:
  src_x   : Bits8
  src_y   : Bits8
  dst_x   : Bits8
  dst_y   : Bits8
  dst_ter : Bits3
  plen    : Bits4
  filler  : Bits89

@bitstruct
class Packet256:
  src_x   : Bits8
  src_y   : Bits8
  dst_x   : Bits8
  dst_y   : Bits8
  dst_ter : Bits3
  plen    : Bits4
  filler  : Bits217

@bitstruct
class Packet512:
  src_x   : Bits8
  src_y   : Bits8
  dst_x   : Bits8
  dst_y   : Bits8
  dst_ter : Bits3
  plen    : Bits4
  filler  : mk_bits(473)

@bitstruct
class Position:
  pos_x : Bits8
  pos_y : Bits8

pkt_dict = {
  32  : Packet32,
  64  : Packet64,
  128 : Packet128,
  256 : Packet256,
  512 : Packet512,
}

@pytest.mark.parametrize(
  'ncores, nbits, channel_lat', [
  ( 4, 32,  0 ),
  ( 4, 32,  1 ),
  ( 4, 64,  0 ),
  ( 4, 64,  1 ),
  ( 4, 128, 0 ),
  ( 4, 128, 1 ),
  ( 4, 256, 0 ),
  ( 4, 256, 1 ),
  ( 4, 512, 0 ),
  ( 4, 512, 1 ),
  ( 8, 32,  0 ),
  ( 8, 32,  1 ),
  ( 8, 64,  1 ),
  ( 8, 128, 1 ),
  ( 8, 256, 1 ),
  ( 8, 512, 1 ),
])
def test_translate( ncores, nbits, channel_lat ):
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

  dut = CMeshTile( Pkt, Position, ncores )

  dut.set_param( 'top.router.input_units*.construct', QueueType=Queue )
  dut.set_param( 'top.channels*.construct', QueueType=Queue, latency=[send_lat, recv_lat] )


  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'CMeshTile_{ncores}c{nbits}b{channel_lat}p' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()
