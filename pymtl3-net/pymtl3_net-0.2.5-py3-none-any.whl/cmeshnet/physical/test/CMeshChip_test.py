'''
==========================================================================
CMeshChip_test.py
==========================================================================
Some simple tests for the CMeshChip.

Author : Yanghui Ou
  Date : Aug 2, 2020
'''
from pymtl3 import *
from pymtl3.passes.backends.verilog import *

from ..CMeshChip import CMeshChip

@bitstruct
class Header64:
  src_x : Bits8
  src_y : Bits8
  dst_x : Bits8
  dst_y : Bits8
  plen  : Bits4
  filler: Bits28

@bitstruct
class Header128:
  src_x  : Bits8
  src_y  : Bits8
  dst_x  : Bits8
  dst_y  : Bits8
  dst_ter: Bits3
  plen   : Bits4
  filler : Bits89

@bitstruct
class Position:
  pos_x : Bits8
  pos_y : Bits8

# def test_translate3x3():
#   assert Header64.nbits == 64
#   assert Position.nbits == 16

#   dut = CMeshChip( Header64, Position, ncols=3, nrows=3 )
#   dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'CMeshChip3x3' )
#   dut.set_metadata( VerilogTranslationImportPass.enable, True )
#   dut.elaborate()
#   dut = VerilogTranslationImportPass()( dut )

#   dut.apply( DefaultPassGroup() )
#   dut.sim_reset()
#   dut.sim_tick()
#   dut.sim_tick()

def test_translate8x8():
  assert Header128.nbits == 128
  assert Position.nbits == 16
  ncols = 8
  nrows = 8

  dut = CMeshChip( Header128, Position, ncols=ncols, nrows=nrows )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'CMeshChip{ncols}x{nrows}' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

def test_translate4x8():
  assert Header128.nbits == 128
  assert Position.nbits == 16
  ncols = 4
  nrows = 8

  dut = CMeshChip( Header128, Position, ncols=ncols, nrows=nrows )
  dut.set_param( 'top.tiles.construct', ncores=8 )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'CMeshChip{ncols}x{nrows}' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

# def test_translate16x16():
#   assert Header64.nbits == 64
#   assert Position.nbits == 16
#   ncols = 16
#   nrows = 16

#   dut = CMeshChip( Header64, Position, ncols=ncols, nrows=nrows )
#   dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'CMeshChip{ncols}x{nrows}' )
#   dut.set_metadata( VerilogTranslationImportPass.enable, True )
#   dut.elaborate()
#   dut = VerilogTranslationImportPass()( dut )

#   dut.apply( DefaultPassGroup() )
#   dut.sim_reset()
#   dut.sim_tick()
#   dut.sim_tick()

