from learns2.parser import SC2ReplayParser
from collections import deque
from collections.abc import Iterator
from typing import List


class EventIterator(Iterator):
    """Groups game events by game loop."""

    def __init__(self, events: List, num_frames: int):
        """
        :param events: raw sequence of game events
        :param num_frames: number of frames to return
        """
        self.events = deque(events)
        self.buffer = None
        self.frame = 0
        self.num_frames = num_frames

    def __next__(self):
        """Returns a list of all game events for the current frame."""
        if self.frame == self.num_frames:
            raise StopIteration
        buf = []
        while self.events and self.events[0]['_gameloop'] == self.frame:
            buf.append(self.events.popleft())
        self.frame += 1
        return buf


class SC2ReplayFeaturizer(object):
    def __init__(self, replay):
        self.parser = SC2ReplayParser(replay)

    def frames(self, n):
        events = self.parser.events()
        itr = EventIterator(events, n)
        return list(itr)

    def hotkey_feature(self, frames: List):
        pass

    def races_feature(self, frames: List):
        pass

    def camera_hotspots_feature(self, frames: List):
        pass
