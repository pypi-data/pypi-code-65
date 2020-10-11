from wendigo import Keys, Point
from wendigo.device.core import Inputs
from wendigo.device.dll import EventSimulator as DllEventSimulator

class EventSimulator():
    """
    Event simulator.
    """
    @classmethod
    def simulate(cls, inputs: Inputs):
        """
        Simulate device event.

        Parameters
        ----------
        inputs: Inputs.
        """
        DllEventSimulator.Simulate(inputs)

    @classmethod
    def key_down(cls, key: Keys, n: int=1):
        """
        Simulate key down.

        Parameters
        ----------
        key: Key.
        n: Number of inputs.
        """
        DllEventSimulator.KeyDown(key, n)

    @classmethod
    def key_up(cls, key: Keys, n: int=1):
        """
        Simulate key up.

        Parameters
        ----------
        key: Key.
        n: Number of inputs.
        """
        DllEventSimulator.KeyUp(key, n)

    @classmethod
    def key_press(cls, key: Keys, n: int=1):
        """
        Simulate key press.

        Parameters
        ----------
        key: Key.
        n: Number of inputs.
        """
        DllEventSimulator.KeyPress(key, n)

    @classmethod
    def type_text(cls, text: str, n: int=1):
        """
        Type text.

        Parameters
        ----------
        text: Text.
        n: Number of inputs.
        """
        DllEventSimulator.TypeText(text, n)

    @classmethod
    def point_relative(cls, position: Point):
        """
        Point a pixel by a relative position.

        Parameters
        ----------
        position: Position.
        """
        DllEventSimulator.PointRelative(position.x, position.y)

    @classmethod
    def point_absolute(cls, position: Point):
        """
        Point a pixel by a absolute position.

        Parameters
        ----------
        position: Position.
        """
        DllEventSimulator.PointAbsolute(position.x, position.y)

    @classmethod
    def tilt(cls, value: int, n: int=1):
        """
        Tilt.

        Parameters
        ----------
        value: Value.
        n: Number of inputs.
        """
        DllEventSimulator.Tilt(value, n)

    @classmethod
    def wheel(cls, value: int, n: int=1):
        """
        Wheel.

        Parameters
        ----------
        value: Value.
        n: Number of inputs.
        """
        DllEventSimulator.Wheel(value, n)