#=========================================================================
# MeshC4E2RouterRTL.py
#=========================================================================
# Simple network-on-chip router, try to connect all the units together
#
# Author : Cheng Tan, Yanghui Ou
#   Date : Mar 8, 2019

from pymtl3 import *
from router.InputUnitRTL import InputUnitRTL
from router.OutputUnitRTL import OutputUnitRTL
from router.Router import Router
from router.SwitchUnitRTL import SwitchUnitRTL
from .MeshC4E2RouteUnitRTL import MeshC4E2RouteUnitRTL

class MeshC4E2RouterRTL( Router ):

  def construct( s, PacketType, PositionType, InputUnitType  = InputUnitRTL, SwitchUnitType = SwitchUnitRTL ):

    super().construct(
      PacketType,
      PositionType,
      12,
      12,
      InputUnitType,
      MeshC4E2RouteUnitRTL,
      SwitchUnitType,
      OutputUnitRTL,
    )
