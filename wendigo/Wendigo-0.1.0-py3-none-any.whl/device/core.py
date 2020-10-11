from collections import namedtuple
from enum import IntEnum
from typing import List, Union
from wendigo import Keys
from wendigo.core import Point
from wendigo.device.dll import DeviceEventArgs, Inputs as DllInputs

class DeviceEvent(IntEnum):
    """
    Device event.
    """
    Nothing    = -1
    KeyDown    =  0
    KeyPress   =  1
    KeyUp      =  2
    MouseMove  =  3
    MouseWheel =  4
    MouseTilt  =  5

class Inputs(DllInputs):
    """
    Inputs.
    """
    def key_down(self, keys: Union[Keys, List[Keys]], n: int=1) -> "Inputs":
        """
        Define inputs for key down.

        Parameters
        ----------
        keys: Keys.
        n: Number of inputs.

        Returns
        -------
        inputs: Inputs.
        """
        super().KeyDown(keys, n)
        return self
        
    def key_up(self, keys: Union[Keys, List[Keys]], n: int=1) -> "Inputs":
        """
        Define inputs for key up.

        Parameters
        ----------
        keys: Keys.
        n: Number of inputs.

        Returns
        -------
        inputs: Inputs.
        """
        super().KeyUp(keys, n)
        return self
        
    def key_press(self, keys: Union[Keys, List[Keys]], n: int=1) -> "Inputs":
        """
        Define inputs for key press.

        Parameters
        ----------
        keys: Keys.
        n: Number of inputs.

        Returns
        -------
        inputs: Inputs.
        """
        super().KeyPress(keys, n)
        return self
        
    def key_press_text(self, texts: Union[str, List[str]], n: int=1) -> "Inputs":
        """
        Define inputs for key press by texts.

        Parameters
        ----------
        texts: Texts.
        n: Number of inputs.

        Returns
        -------
        inputs: Inputs.
        """
        super().KeyPress(texts, n)
        return self

    def tilt(self, value: int, n: int=1) -> "Inputs":
        """
        Define inputs for mouse tilt.

        Parameters
        ----------
        value: Value.
        n: Number of inputs.

        Returns
        -------
        inputs: Inputs.
        """
        super().Tilt(value, n)
        return self
        
    def wheel(self, value: int, n: int=1) -> "Inputs":
        """
        Define inputs for mouse wheel.

        Parameters
        ----------
        value: Value.
        n: Number of inputs.

        Returns
        -------
        inputs: Inputs.
        """
        super().Wheel(value, n)
        return self

key_state = namedtuple("key_state", ("target", "keys"))
mouse_state = namedtuple("mouse_state", ("target", "position", "scroll"))

class DeviceState:
    """
    Device state.
    """
    def __init__(self, e: DeviceEventArgs):
        """
        Initialize.

        Parameters
        ----------
        e: Device event args.
        """
        state = e.State

        self.event_type = DeviceEvent(state.DeviceEvent)
        self.key = key_state(
            target=state.Key.Target,
            keys={entry.Key: entry.Value for entry in state.Key.Keys},
        )

        position = state.Mouse.Position
        scroll = state.Mouse.Scroll
        
        self.mouse = mouse_state(
            target=state.Mouse.Target,
            position=Point(position.X, position.Y),
            scroll=Point(scroll.X, scroll.Y),
        )