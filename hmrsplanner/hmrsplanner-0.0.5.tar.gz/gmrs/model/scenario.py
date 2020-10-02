
from .mission import Mission
from .unit import Unit
from .world_map import WorldMap


class Scenario:
    mission: Mission = None
    units: [Unit] = None
    world_map: WorldMap = None
