'''
==========================================================================
BidirectionalChannelRTL.py
==========================================================================
Bi-directional channels that is composed of two uni-directional channel.

Author: Yanghui Ou
  Date: Aug 13, 2020
'''
from pymtl3 import *
from pymtl3.stdlib.queues import NormalQueueRTL

from ocnlib.ifcs.CreditIfc import CreditRecvIfcRTL, CreditSendIfcRTL

from .ChannelCreditRTL import ChannelCreditRTL

class BidirectionalChannelCreditRTL( Component ):

  def construct( s, PacketType, latency=[0,0] ):

    # Interface

    s.recv = [ CreditRecvIfcRTL( PacketType, vc=2 ) for _ in range(2) ]
    s.send = [ CreditSendIfcRTL( PacketType, vc=2 ) for _ in range(2) ]

    s.chnls = [ ChannelCreditRTL( PacketType, vc=2, latency=latency[i] ) for i in range(2) ]

    for i in range(2):
      s.recv[i] //= s.chnls[i].recv
      s.send[i] //= s.chnls[i].send

  def line_trace( s ):
    return f'{s.recv[0]}|{s.recv[1]}(){s.send[0]}{s.send[1]}'
