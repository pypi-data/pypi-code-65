from typing import Callable
from wendigo.system import Action
from wendigo.process.dll import TimeKeeper as DllTimeKeeper

class TimeKeeper(DllTimeKeeper):
    """
    Time keeper.
    """
    @classmethod
    def listen(cls, name: str, event_handler: Callable[[], None], interval: int):
        """
        Listen for timer event.

        Parameters
        ----------
        name: Name.
        event_handler: Event handler.
        interval: Interval in milliseconds.
        """
        cls.Listen(name, Action(event_handler), interval)

    @classmethod
    def unlisten(cls, name: str):
        """
        Unlisten for timer event.

        Parameters
        ----------
        name: Name.
        """
        cls.Unlisten(name)