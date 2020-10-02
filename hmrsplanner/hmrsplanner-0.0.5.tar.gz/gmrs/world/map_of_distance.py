
class MapOfDistance():
    _map = {}

    def add_direct_segment(self, locationA, locationB, distance):
        if self._map[locationA.name] is None:
            self._map[locationA.name] = {}
        self._map[locationA.name][locationB.name] = distance
