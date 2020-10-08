'''
==========================================================================
TorusTile_test.py
==========================================================================
Some simple tests for the TorusTile.

Author : Yanghui Ou
  Date : Aug 12, 2020
'''
import pytest
from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from ocnlib.rtl.queues import NormalQueueRTL as Queue

from ..TorusTile import TorusTile

@bitstruct
class Packet32:
  src_x   : Bits4
  src_y   : Bits4
  dst_x   : Bits4
  dst_y   : Bits4
  vc_id   : Bits1
  payload : Bits15

@bitstruct
class Packet64:
  src_x  : Bits4
  src_y  : Bits4
  dst_x  : Bits4
  dst_y  : Bits4
  vc_id  : Bits1
  dst_ter: Bits3
  plen   : Bits4
  filler : Bits40

@bitstruct
class Packet128:
  src_x   : Bits4
  src_y   : Bits4
  dst_x   : Bits4
  dst_y   : Bits4
  vc_id   : Bits1
  dst_ter : Bits3
  plen    : Bits4
  filler  : Bits104

@bitstruct
class Packet256:
  src_x   : Bits4
  src_y   : Bits4
  dst_x   : Bits4
  dst_y   : Bits4
  vc_id   : Bits1
  dst_ter : Bits2
  plen    : Bits4
  filler  : Bits233

@bitstruct
class Packet512:
  src_x   : Bits4
  src_y   : Bits4
  dst_x   : Bits4
  dst_y   : Bits4
  vc_id   : Bits1
  dst_ter : Bits3
  plen    : Bits4
  filler  : mk_bits(488)

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

  credit_line = 3 + channel_lat

  dut = TorusTile( Pkt, Position, credit_line=credit_line, latency=channel_lat )

  dut.set_param( 'top.router.input_units*.construct', QueueType=Queue )
  dut.set_param( 'top.channels*.construct', latency=[send_lat, recv_lat]  )

  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'TorusTile_{nbits}b{channel_lat}p' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()
