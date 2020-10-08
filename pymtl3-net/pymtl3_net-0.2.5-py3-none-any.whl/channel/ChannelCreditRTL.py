'''
==========================================================================
ChannelCreditRTL.py
==========================================================================
Channel for credit based flow control.

Author : Yanghui Ou
  Date : Aug 13, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.basic_rtl import Reg
from ocnlib.ifcs.CreditIfc import CreditRecvIfcRTL, CreditSendIfcRTL

class ChannelCreditRTL( Component ):

  def construct( s, PhitType, vc=2, latency=0 ):

    # Interface

    s.recv = CreditRecvIfcRTL( PhitType, vc=vc )
    s.send = CreditSendIfcRTL( PhitType, vc=vc )

    if latency > 0:

      s.msg_regs = [ Reg( PhitType    ) for _ in range(latency) ]
      s.en_regs  = [ Reg( Bits1       ) for _ in range(latency) ]
      # s.yum_regs = [ Reg( mk_bits(vc) ) for _ in range(latency) ]

      s.msg_regs[0].in_ //= s.recv.msg
      s.en_regs[0].in_  //= s.recv.en
      # for i in range( vc ):
      #   s.yum_regs[0].in_[i] //= s.send.yum[i]

      for i in range( latency - 1 ):
        s.msg_regs[i+1].in_ //= s.msg_regs[i].out
        s.en_regs[i+1].in_  //= s.en_regs[i].out
        # s.yum_regs[i+1].in_ //= s.yum_regs[i].out

      s.send.msg //= s.msg_regs[-1].out
      s.send.en  //= s.en_regs[-1].out
      for i in range( vc ):
        # s.recv.yum[i] //= s.yum_regs[-1].out[i]
        s.recv.yum[i] //= s.send.yum[i]

    else:

      assert latency == 0
      s.recv //= s.send

  def line_trace( s ):
    return f'{s.recv}(){s.send}'
