'''
==========================================================================
PitonTile_test.py
==========================================================================
Some simple tests for the PitonTile.

Author : Yanghui Ou
  Date : July 30, 2020
'''
from pymtl3 import *
from pymtl3.passes.backends.verilog import *
from ocnlib.rtl.queues import NormalQueueRTL as Queue

from ..PitonTile import PitonTile


@bitstruct
class Position:
  pos_x : Bits8
  pos_y : Bits8

def test_translate():
  assert Position.nbits == 16

  dut = PitonTile( Position )
  dut.set_param( 'top.router.input_units*.construct', QueueType=Queue )
  dut.set_param( 'top.router.output_units*.construct', QueueType=None, data_gating=False )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'PitonTile' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )

  dut.apply( DefaultPassGroup() )
  dut.sim_reset()
  dut.sim_tick()
  dut.sim_tick()

