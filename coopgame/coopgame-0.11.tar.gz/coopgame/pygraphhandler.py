from coopgame.colors import Color
import pygame
from coopgraph.graphs import Graph
from coopstructs.vectors import Vector2
import coopgame.pygamehelpers as help
from typing import Callable

class PyGraphHandler:
    def _draw_graph_edges(self, surface: pygame.Surface, graph: Graph, coordinate_converter: Callable[[Vector2], Vector2] = None, enabled_color: Color = None, disabled_color: Color = None, draw_scale_matrix = None):

        if not coordinate_converter:
            coordinate_converter = lambda x: x

        if not enabled_color:
            enabled_color = Color.BLUE

        if not disabled_color:
            disabled_color = Color.GREY

        for edge in graph.edges():
            start = coordinate_converter(edge.start.pos)
            end = coordinate_converter(edge.end.pos)
            scaled_pos = help.scaled_points_of_points([start, end], draw_scale_matrix=draw_scale_matrix)
            color = enabled_color if edge.enabled() else disabled_color
            pygame.draw.line(surface, color.value, (scaled_pos[0][0], scaled_pos[0][1]), (scaled_pos[1][0], scaled_pos[1][1]))

    def _draw_graph_nodes(self, surface: pygame.Surface, graph: Graph, coordinate_converter: Callable[[Vector2], Vector2] = None, color: Color = None, radius: int = 1, width: int = 0, draw_scale_matrix = None):
        if not coordinate_converter:
            coordinate_converter = lambda x: x

        if not color:
            color = Color.ORANGE

        for node in graph.nodes():
            position = coordinate_converter(node.pos)
            scaled_pos = help.scaled_points_of_points([position], draw_scale_matrix=draw_scale_matrix)
            position = (int(scaled_pos[0][0]), int(scaled_pos[0][1]))

            pygame.draw.circle(surface, color.value, position, radius, width)

    def draw_to_surface(self, surface: pygame.Surface, graph: Graph,
                        coordinate_converter: Callable[[Vector2], Vector2] = None,
                        node_color: Color = None,
                        enabled_edge_color: Color = None,
                        disabled_edge_color: Color = None,
                        draw_scale_matrix = None):
        if not coordinate_converter:
            coordinate_converter = lambda x: x

        self._draw_graph_edges(surface, graph=graph, coordinate_converter=coordinate_converter, enabled_color=enabled_edge_color, disabled_color=disabled_edge_color, draw_scale_matrix=draw_scale_matrix)
        self._draw_graph_nodes(surface, graph=graph, coordinate_converter=coordinate_converter, color=node_color, draw_scale_matrix=draw_scale_matrix)
