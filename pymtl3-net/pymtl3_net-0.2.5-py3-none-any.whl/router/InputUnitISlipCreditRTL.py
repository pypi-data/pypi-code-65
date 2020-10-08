"""
==========================================================================
InputUnitISlipCreditRTL.py
==========================================================================
An input unit with a credit based interface.

Author : Yanghui Ou
  Date : Aug 17, 2020
"""
from pymtl3 import *
from pymtl3.stdlib.ifcs import GiveIfcRTL
from pymtl3.stdlib.basic_rtl.arbiters import RoundRobinArbiterEn
from pymtl3.stdlib.basic_rtl import Encoder
from pymtl3.stdlib.queues import NormalQueueRTL
from ocnlib.ifcs.CreditIfc import CreditRecvIfcRTL


class InputUnitISlipCreditRTL( Component ):

  def construct( s, PacketType, QueueType = NormalQueueRTL,
                 vc=2, credit_line=2 ):

    # Local paramters
    s.vc        = vc
    s.sel_width = clog2( vc )

    # Interface
    s.recv = CreditRecvIfcRTL( PacketType, vc=vc )
    s.give = GiveIfcRTL( PacketType )

    # Components

    s.buffers = [ QueueType( PacketType, num_entries=credit_line )
                  for _ in range( vc ) ]

    s.recv_yum_wire = Wire( vc )

    for i in range( vc ):
      s.buffers[i].enq.msg //= s.recv.msg
    #   s.buffers[i].deq     //= s.give[i]
    #   s.recv.yum[i]        //= s.give[i].en

    s.arbiter = RoundRobinArbiterEn( vc )
    s.encoder = Encoder( vc, s.sel_width )

    s.arbiter.en //= lambda: s.give.en
    s.arbiter.grants //= s.encoder.in_

    for i in range( vc ):
      s.buffers[i].deq.rdy //= s.arbiter.reqs[i]

    s.give.rdy //= lambda: s.arbiter.grants > 0
    s.give.ret //= lambda: s.buffers[ s.encoder.out ].deq.ret

    @update
    def up_buffers_deq():
      for i in range( vc ):
        s.buffers[i].deq.en @= 0
      s.buffers[ s.encoder.out ].deq.en @= s.give.en

    @update
    def up_yum_wire():
      for i in range( vc ):
        s.recv_yum_wire[i] @= 0
        s.recv_yum_wire[ s.encoder.out ] @= s.give.en

    @update_ff
    def up_recv_yum():
      for i in range( vc ):
        s.recv.yum[i] <<= s.recv_yum_wire[i]

    @update
    def up_enq():
      if s.recv.en:
        for i in range( vc ):
          s.buffers[i].enq.en @= s.recv.msg.vc_id == i
      else:
        for i in range( vc ):
          s.buffers[i].enq.en @= 0

  def line_trace( s ):
    # return "{}({}){}".format(
    #   s.recv,
    #   ",".join([ str(s.buffers[i].count) for i in range( s.vc ) ]),
    #   # "|".join([ str(s.give[i]) for i in range( s.vc ) ]),
    #   s.give,
    # )
    return f'{s.recv}(<{",".join([ str(s.buffers[i].count) for i in range( s.vc ) ])}>||{s.arbiter.reqs.bin()}){s.give}'