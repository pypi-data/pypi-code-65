'''
==========================================================================
ubmark_test.py
==========================================================================
'''
from itertools import product
import pytest
from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from ocnlib.rtl.queues import NormalQueueRTL as Queue

from ..XbarRTL import XbarRTL

@bitstruct
class Packet32:
  src    : Bits8
  dst    : Bits8
  plen   : Bits4
  filler : Bits12

@bitstruct
class Packet64:
  src    : Bits8
  dst    : Bits8
  plen   : Bits4
  filler : Bits44

@bitstruct
class Packet128:
  src    : Bits8
  dst    : Bits8
  plen   : Bits4
  filler : Bits108

@bitstruct
class Packet256:
  src    : Bits8
  dst    : Bits8
  plen   : Bits4
  filler : Bits236

@bitstruct
class Packet512:
  src    : Bits8
  dst    : Bits8
  plen   : Bits4
  filler : mk_bits(492)

pkt_dict = {
  32  : Packet32,
  64  : Packet64,
  128 : Packet128,
  256 : Packet256,
  512 : Packet512,
}

@pytest.mark.parametrize(
  'radix, nbits', product(
  [ 2, 4, 6, 8, 10, 12, 14, 16 ],
  [ 32, 64, 128, 256, 512 ],
))
def test_ubmark( radix, nbits ):
  Pkt = pkt_dict[ nbits ]
  assert Pkt.nbits == nbits

  dut = XbarRTL( Pkt, radix, radix )
  dut.set_param( 'top.input_units*.construct', QueueType=Queue )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'Xbar_{radix}r{nbits}b' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()
