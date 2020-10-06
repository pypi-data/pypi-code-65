from typing import Callable

from dendroid.core.hints import (Item,
                                 Key,
                                 Order,
                                 Value)
from dendroid.core.maps import Map
from dendroid.core.sets import Set

Key = Key
Value = Value
Item = Item
Order = Order
Map = Map
Set = Set
MapFactory = Callable[..., Map]
SetFactory = Callable[..., Set]
