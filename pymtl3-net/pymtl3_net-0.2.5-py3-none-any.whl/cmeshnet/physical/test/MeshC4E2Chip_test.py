'''
==========================================================================
MeshChip_C4E2test.py
==========================================================================
Some simple tests for the MeshC4E2Chip.

Author : Yanghui Ou
  Date : Aug 2, 2020
'''
from pymtl3 import *
from pymtl3.passes.backends.verilog import *

from ..MeshC4E2Chip import MeshC4E2Chip

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

# def test_translate3x3():
#   assert Header64.nbits == 64
#   assert Position.nbits == 16

#   dut = MeshC4E2Chip( Header64, Position, ncols=3, nrows=3 )
#   dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'MeshChiC4E2p3x3' )
#   dut.set_metadata( VerilogTranslationImportPass.enable, True )
#   dut.elaborate()
#   dut = VerilogTranslationImportPass()( dut )

#   dut.apply( DefaultPassGroup() )
#   dut.sim_reset()
#   dut.sim_tick()
#   dut.sim_tick()

def test_translate8x8():
  assert Packet64.nbits == 64
  assert Position.nbits == 8
  ncols = 8
  nrows = 8

  dut = MeshC4E2Chip( Packet64, Position, ncols=ncols, nrows=nrows )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'MeshC4E2Chip{ncols}x{nrows}_64b' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

# def test_translate4x8():
#   assert Header128.nbits == 128
#   assert Position.nbits == 16
#   ncols = 4
#   nrows = 8

#   dut = MeshC4E2Chip( Header128, Position, ncols=ncols, nrows=nrows )
#   dut.set_param( 'top.tiles.construct', ncores=8 )
#   dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'MeshC4E2Chip{ncols}x{nrows}' )
#   dut.set_metadata( VerilogTranslationImportPass.enable, True )
#   dut.elaborate()
#   dut = VerilogTranslationImportPass()( dut )

#   dut.apply( DefaultPassGroup() )
#   dut.sim_reset()
#   dut.sim_tick()
#   dut.sim_tick()

