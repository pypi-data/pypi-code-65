from .graph import Graph

class Walk(Graph):
    """
        This class adapts OSM or OSRM walk routing

        It should inherit all the nodes available, then apply OSM - OSRM routing API and finally filter accordingly with
        the TP config for the maximum walking distance or time.
    """
