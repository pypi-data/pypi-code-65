from typing import List
from wendigo import Keys
from wendigo.device.dll import EventImitator as DllEventImitator

class EventImitator():
    """
    Event imitator.
    """
    @classmethod
    def record(cls, path: str, start_keys: List[Keys], stop_keys: List[Keys]):
        """
        Record device events.
        Key events for start_keys and stop_keys are ignored.

        Parameters
        ----------
        path: File path.
        start_keys: Keys to start recording.
        stop_keys: Keys to stop recording.
        """
        DllEventImitator.Record(path, start_keys, stop_keys)

    @classmethod
    def play(cls, path: str, start_keys: List[Keys], stop_keys: List[Keys]):
        """
        Play device events.

        Parameters
        ----------
        path: File path.
        start_keys: Keys to start playing.
        stop_keys: Keys to stop playing.
        """
        DllEventImitator.Play(path, start_keys, stop_keys)