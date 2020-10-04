from . import Mission


class Scenario:
    def __init__(self):
        self.mission: Mission = None
        self.robots = None
        self.world = None
        self.events = []
