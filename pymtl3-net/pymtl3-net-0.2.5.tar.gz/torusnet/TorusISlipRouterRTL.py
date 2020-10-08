"""
==========================================================================
TorusRouterISlipRTL.py
==========================================================================
Torus router RTL model.

Author : Yanghui, Ou, Cheng Tan
  Date : June 30, 2019
"""
from ocnlib.ifcs.CreditIfc import CreditRecvIfcRTL, CreditSendIfcRTL
from pymtl3 import *
from router.InputUnitISlipCreditRTL import InputUnitISlipCreditRTL
from router.OutputUnitCreditRTL import OutputUnitCreditRTL
from router.SwitchUnitRTL import SwitchUnitRTL

from .DORYTorusRouteUnitRTL import DORYTorusRouteUnitRTL


class TorusISlipRouterRTL( Component ):

  def construct( s, PacketType, PositionType,
                    InputUnitType=InputUnitISlipCreditRTL,
                    RouteUnitType=DORYTorusRouteUnitRTL,
                    SwitchUnitType=SwitchUnitRTL,
                    OutputUnitType=OutputUnitCreditRTL,
                    ncols=2, nrows=2, vc=2, credit_line=2,
  ):

    s.num_inports  = 5
    s.num_outports = 5
    s.vc = vc
    PhitBitsType = mk_bits( PacketType.nbits )

    # Interface

    s.pos  = InPort( PositionType )
    s.recv = [ CreditRecvIfcRTL( PhitBitsType, s.vc ) for _ in range( s.num_inports  ) ]
    s.send = [ CreditSendIfcRTL( PhitBitsType, s.vc ) for _ in range( s.num_outports ) ]

    # Components

    s.input_units  = [ InputUnitType( PacketType, vc=vc, credit_line=credit_line )
                      for _ in range( s.num_inports ) ]

    s.route_units  = [ RouteUnitType( PacketType, PositionType, ncols, nrows )
                      for _ in range( s.num_inports ) ]

    s.switch_units = [ SwitchUnitType( PacketType, s.num_inports )
                      for _ in range( s.num_outports ) ]

    s.output_units = [ OutputUnitType( PacketType )
                      for _ in range( s.num_outports ) ]

    # Connection

    for i in range( s.num_inports ):
      # s.recv[i] //= s.input_units[i].recv
      s.input_units[i].give //= s.route_units[i].get
      s.pos                 //= s.route_units[i].pos


    for i in range( s.num_inports ):
      for j in range( s.num_outports ):
        s.route_units[i].give[j] //= s.switch_units[j].get[i]

    for j in range( s.num_outports ):
      s.switch_units[j].give //= s.output_units[j].get
      # s.output_units[j].send //= s.send[j]

    # Convert input/out bit/bitstruct
    @update
    def up_bits2bitstrcut():
      for i in range( s.num_inports ):
        s.input_units[i].recv.msg @= s.recv[i].msg
        s.input_units[i].recv.en  @= s.recv[i].en
        for j in range( s.vc ):
          s.recv[i].yum[j] @= s.input_units[i].recv.yum[j]

      for i in range( s.num_outports ):
        s.send[i].msg @= s.output_units[i].send.msg
        s.send[i].en  @= s.output_units[i].send.en
        for j in range( s.vc ):
          s.output_units[i].send.yum[j] @=s.send[i].yum[j]

  # Line trace

  def line_trace( s ):
    return "{}({}){}".format(
      "|".join( [ f"{str(x)}" for x in s.recv ] ),
      s.pos,
      "|".join( [ f"{str(x)}" for x in s.send ] )
    )
    # return f'{s.recv[4]}({s.input_units[4].line_trace()})'

  def elaborate_physical( s ):
    s.dim.w = 50
    s.dim.h = 50
