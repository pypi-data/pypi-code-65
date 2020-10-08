'''
==========================================================================
TorusChip_test.py
==========================================================================
Some simple tests for the TorusChip.

Author : Yanghui Ou
  Date : Aug 2, 2020
'''
from pymtl3 import *
from pymtl3.passes.backends.verilog import *

from ..TorusChip import TorusChip

@bitstruct
class Header64:
  src_x : Bits4
  src_y : Bits4
  dst_x : Bits4
  dst_y : Bits4
  vc_id : Bits1
  plen  : Bits4
  filler: Bits43

@bitstruct
class Header32:
  src_x : Bits4
  src_y : Bits4
  dst_x : Bits4
  dst_y : Bits4
  plen  : Bits4
  vc_id : Bits1
  filler: Bits11


@bitstruct
class Position:
  pos_x : Bits4
  pos_y : Bits4

def test_translate3x3():
  assert Header64.nbits == 64
  assert Position.nbits == 16

  dut = TorusChip( Header64, Position, ncols=3, nrows=3 )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'TorusChip3x3' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

def test_translate8x8():
  assert Header64.nbits == 64
  assert Position.nbits == 8
  ncols = 8
  nrows = 8

  dut = TorusChip( Header64, Position, ncols=ncols, nrows=nrows )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'TorusChip{ncols}x{nrows}_64b' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

def test_translate16x16():
  assert Header32.nbits == 32
  assert Position.nbits == 8
  ncols = 16
  nrows = 16

  dut = TorusChip( Header32, Position, ncols=ncols, nrows=nrows )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'TorusChip{ncols}x{nrows}_32b' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

def test_translate16x16_64b():
  assert Header64.nbits == 64
  assert Position.nbits == 8
  ncols = 16
  nrows = 16

  dut = TorusChip( Header64, Position, ncols=ncols, nrows=nrows )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'TorusChip{ncols}x{nrows}_64b' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()


def test_translate2x2():
  assert Header32.nbits == 32
  assert Position.nbits == 8
  ncols = 2
  nrows = 2

  dut = TorusChip( Header32, Position, ncols=ncols, nrows=nrows )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'TorusChip{ncols}x{nrows}_32b' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()
