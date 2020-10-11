from typing import Callable, List
from wendigo import Keys
from wendigo.device import DeviceState
from wendigo.device.dll import EventDispatcher as DllEventDispatcher, \
     DeviceEventArgs, DeviceEventHandler
from wendigo.logger import Logger

class EventDispatcher:
    """
    Event dispatcher.
    """
    @classmethod
    def get_event_handler(cls, event_handler: Callable[[DeviceState], None]) -> DeviceEventHandler:
        """
        Get an event handler.

        Parameters
        ----------
        event_handler: Event Handler.

        Returns
        -------
        device_event_handler: Device event handler.
        """
        def wrapper(e: DeviceEventArgs):
            try:
                event_handler(DeviceState(e))
            except:
                Logger.exception("An exception raised in event hadler")
        return DeviceEventHandler(wrapper)

    @classmethod
    def get_event_handler_once(cls, name: str, event_handler: Callable[[DeviceState], None]) -> DeviceEventHandler:
        """
        Get an event handler which is called only once.

        Parameters
        ----------
        name: Name.
        event_handler: Event handler.

        Returns
        -------
        device_event_handler: Device event handler.
        """
        def wrapper(e: DeviceEventArgs):
            try:
                cls.unlisten(name)
                event_handler(DeviceState(e))
            except:
                Logger.exception("An exception raised in event hadler")
        return DeviceEventHandler(wrapper)

    @classmethod
    def key_down(cls, name: str, keys: List[Keys], event_handler: Callable[[DeviceState], None], for_system: bool=False):
        """
        Listen for key down.

        Parameters
        ----------
        name: Name.
        keys: Keys.
        event_handler: Event handler.
        for_system: The event is for system or not.
        """
        DllEventDispatcher.KeyDown(name, keys, cls.get_event_handler(event_handler), for_system)

    @classmethod
    def key_down_once(cls, name: str, keys: List[Keys], event_handler: Callable[[DeviceState], None], for_system: bool=False):
        """
        Listen for key down which is called only once.

        Parameters
        ----------
        name: Name.
        keys: Keys.
        event_handler: Event handler.
        for_system: The event is for system or not.
        """
        DllEventDispatcher.KeyDown(name, keys, cls.get_event_handler_once(name, event_handler), for_system)

    @classmethod
    def key_up(cls, name: str, keys: List[Keys], event_handler: Callable[[DeviceState], None], for_system: bool=False):
        """
        Listen for key up.

        Parameters
        ----------
        name: Name.
        keys: Keys.
        event_handler: Event handler.
        for_system: The event is for system or not.
        """
        DllEventDispatcher.KeyUp(name, keys, cls.get_event_handler(event_handler), for_system)

    @classmethod
    def key_up_once(cls, name: str, keys: List[Keys], event_handler: Callable[[DeviceState], None], for_system: bool=False):
        """
        Listen for key up which is called only once.

        Parameters
        ----------
        name: Name.
        keys: Keys.
        event_handler: Event handler.
        for_system: The event is for system or not.
        """
        DllEventDispatcher.KeyUp(name, keys, cls.get_event_handler_once(name, event_handler), for_system)
    
    @classmethod
    def key_press(cls, name: str, keys: List[Keys], event_handler: Callable[[DeviceState], None], for_system: bool=False):
        """
        Listen for key press.

        Parameters
        ----------
        name: Name.
        keys: Keys.
        event_handler: Event handler.
        for_system: The event is for system or not.
        """
        DllEventDispatcher.KeyPress(name, keys, cls.get_event_handler(event_handler), for_system)
    
    @classmethod
    def key_press_once(cls, name: str, keys: List[Keys], event_handler: Callable[[DeviceState], None], for_system: bool=False):
        """
        Listen for key press which is called only once.

        Parameters
        ----------
        name: Name.
        keys: Keys.
        event_handler: Event handler.
        for_system: The event is for system or not.
        """
        DllEventDispatcher.KeyPress(name, keys, cls.get_event_handler_once(name, event_handler), for_system)

    @classmethod
    def mouse_move(cls, name: str, event_handler: Callable[[DeviceState], None], for_system: bool=False):
        """
        Listen for mouse move.

        Parameters
        ----------
        name: Name.
        event_handler: Event handler.
        for_system: The event is for system or not.
        """
        DllEventDispatcher.MouseMove(name, cls.get_event_handler(event_handler), for_system)
    
    @classmethod
    def mouse_move_once(cls, name: str, event_handler: Callable[[DeviceState], None], for_system: bool=False):
        """
        Listen for mouse move which is called only once.

        Parameters
        ----------
        name: Name.
        event_handler: Event handler.
        for_system: The event is for system or not.
        """
        DllEventDispatcher.MouseMove(name, cls.get_event_handler_once(name, event_handler), for_system)
    
    @classmethod
    def mouse_wheel(cls, name: str, event_handler: Callable[[DeviceState], None], for_system: bool=False):
        """
        Listen for mouse wheel.

        Parameters
        ----------
        name: Name.
        event_handler: Event handler.
        for_system: The event is for system or not.
        """
        DllEventDispatcher.MouseWheel(name, cls.get_event_handler(event_handler), for_system)
    
    @classmethod
    def mouse_wheel_once(cls, name: str, event_handler: Callable[[DeviceState], None], for_system: bool=False):
        """
        Listen for mouse wheel which is called only once.

        Parameters
        ----------
        name: Name.
        event_handler: Event handler.
        for_system: The event is for system or not.
        """
        DllEventDispatcher.MouseWheel(name, cls.get_event_handler_once(name, event_handler), for_system)
    
    @classmethod
    def mouse_tilt(cls, name: str, event_handler: Callable[[DeviceState], None], for_system: bool=False):
        """
        Listen for mouse tilt.

        Parameters
        ----------
        name: Name.
        event_handler: Event handler.
        for_system: The event is for system or not.
        """
        DllEventDispatcher.MouseTilt(name, cls.get_event_handler(event_handler), for_system)
    
    @classmethod
    def mouse_tilt_once(cls, name: str, event_handler: Callable[[DeviceState], None], for_system: bool=False):
        """
        Listen for mouse tilt which is called only once.

        Parameters
        ----------
        name: Name.
        event_handler: Event handler.
        for_system: The event is for system or not.
        """
        DllEventDispatcher.MouseTilt(name, cls.get_event_handler_once(name, event_handler), for_system)

    @classmethod
    def unlisten(cls, name: str, for_system: bool=False):
        """
        Unlisten for device event.

        Parameters
        ----------
        name: Name.
        for_system: The event is for system or not.
        """
        DllEventDispatcher.Unlisten(name, for_system)