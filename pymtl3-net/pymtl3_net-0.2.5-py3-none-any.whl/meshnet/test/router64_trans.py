from pymtl3 import *
from pymtl3.passes.backends.verilog import *

from ocnlib.ifcs.packets import mk_mesh_pkt
from ocnlib.ifcs.positions import mk_mesh_pos
from router.InputUnitRTL import InputUnitRTL
from meshnet.MeshRouterRTL import MeshRouterRTL
from meshnet.DORYMeshRouteUnitRTL import DORYMeshRouteUnitRTL

def test_translate():
  Pkt = mk_mesh_pkt( 256, 256, opaque_nbits=8, payload_nbits=24 )
  Pos = mk_mesh_pos( 256, 256 )
  assert Pkt.nbits == 64
  assert Pos.nbits == 16
  
  dut = MeshRouterRTL( Pkt, Pos, InputUnitType=InputUnitRTL,  RouteUnitType=DORYMeshRouteUnitRTL )
  dut.set_metadata( VerilogTranslationPass.explicit_module_name, f'MeshRouter64' )
  dut.set_metadata( VerilogTranslationImportPass.enable, True )
  dut.elaborate()
  dut = VerilogTranslationImportPass()( dut )
  dut.apply( DefaultPassGroup() )
