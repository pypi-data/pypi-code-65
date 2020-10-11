from typing import List
from wendigo import Keys
from wendigo.application import Wendigo as DllWendigo
from wendigo.device import EventDispatcher, EventImitator, EventSimulator
from wendigo.logger import Logger
from wendigo.process import TimeKeeper
from wendigo.screen import FormController, TargetMarker, TargetSeeker, TextReader
from wendigo.system import EventHandler, Keys

class Wendigo:
    """
    Wendigo.
    """
    event_dispatcher = EventDispatcher
    event_imitator = EventImitator
    event_simulator = EventSimulator

    form_controller = FormController
    target_marker = TargetMarker
    target_seeker = TargetSeeker
    text_reader = TextReader

    time_keeper = TimeKeeper

    @classmethod
    def notify(cls, title: str, text: str, timeout: int=1):
        """
        Show a baloon tip.

        Parameters
        ----------
        title: Title.
        text: Text.
        timeout: Timeout.
        """
        DllWendigo.Notify(title, text, timeout)

    @classmethod
    def add_exit(cls, keys: List[Keys], caption_tasktray: str, caption_handler: str) -> str:
        """
        Add exit.

        Parameters
        ----------
        keys: Keys to exit.
        caption_tasktray: Caption for the tasktray item to exit.
        caption_handler: Caption for the key down event handler to exit.

        Returns
        -------
        caption_tasktray: Caption for the tasktray item to exit.
        """
        caption = "+".join([k.get_name() for k in keys])

        # Add a key down event handler to exit.
        Logger.info(caption_handler.format(keys=caption))
        cls.event_dispatcher.key_down("exit", keys, lambda state: cls.exit(), for_system=True)

        return caption_tasktray.format(keys=caption)

    @classmethod
    def run(cls, name: str=None, icon_path: str=None, exit_keys: List[Keys]=[Keys.LShiftKey, Keys.RShiftKey],
        exit_caption_tasktray: str="Exit ({keys})", exit_caption_handler: str="* Press {keys} to exit"):
        """
        Run.

        Parameters
        ----------
        name: Name.
        icon_path: Icon file path.
        exit_keys: Keys to exit.
        exit_caption_tasktray: Caption for the tasktray item to exit.
        exit_caption_handler: Caption for the key down event handler to exit.
        """
        exit_caption = cls.add_exit(exit_keys, exit_caption_tasktray, exit_caption_handler)

        DllWendigo.Run(name, icon_path, exit_caption)

    @classmethod
    def exit(cls):
        """
        Exit.
        """
        DllWendigo.Exit()