from coopgraph.grids import GridSystem
from coopgraph.dataStructs import GridPoint
from coopstructs.geometry import Rectangle
import pygame
from coopgame.colors import Color
from typing import Dict, Callable
from coopgame.enums import GridDrawType
import coopgame.pygamehelpers as help
from typing import List
from coopstructs.vectors import Vector2
import numpy as np

class PyGridHandler:

    def __init__(self):
        self.hover_grid_pos = None

    def _check_and_handle_hover_grid_change(self, old_hover: Vector2, new_hover: Vector2, handlers: List[Callable[[Vector2, Vector2], None]]):
        if new_hover != self.hover_grid_pos:
            [handler(old_hover, new_hover) for handler in handlers or []]

    def handle_hover_over(self, grid: GridSystem, area_rect: Rectangle,  on_hover_handlers: List[Callable[[Vector2], None]] = None, on_hover_changed_handlers: List[Callable[[Vector2, Vector2], None]] = None, draw_scale_matrix = None):
        # get hovered grid pos
        mouse_pos = help.mouse_pos_as_vector()
        new_hover = self.get_mouse_grid_pos(area_rect, mouse_pos, grid.grid_from_coord, draw_scale_matrix)

        # check and handle when hover grid pos changed
        self._check_and_handle_hover_grid_change(old_hover=self.hover_grid_pos, new_hover=new_hover, handlers=on_hover_changed_handlers)

        # Update the grid pos
        self.hover_grid_pos = new_hover

        # handle grid hover
        [handler(self.hover_grid_pos) for handler in on_hover_handlers or []]

    def grid_box_rectangle(self, width, height, grid:GridSystem, margin: int = 1) -> Rectangle:

        grid_box_height = height / grid.nRows - margin
        grid_box_width = width / grid.nColumns - margin

        return Rectangle(x=0, y=0, height=grid_box_height, width=grid_box_width)


    def draw_overlay_to_surface(self
             , surface:pygame.Surface
             , grid: GridSystem
             , margin: int = 1
             , highlight_grid_cells: Dict[Vector2, Color] = None
             , outlined_grid_cells: Dict[Vector2, Color] = None
             , draw_scale_matrix = None
                                ):
        grid_box_rect = self.grid_box_rectangle(width=surface.get_width(), height=surface.get_height(), grid=grid, margin=margin)
        self._draw_highlighted_grids(surface=surface
                                    , grid_box_rect=grid_box_rect
                                    , highlight_grid_cells=highlight_grid_cells
                                    , margin=margin
                                    , draw_scale_matrix = draw_scale_matrix)
        self._draw_outlined_grids(surface=surface
                                    , grid_box_rect=grid_box_rect
                                    , outlined_grid_cells=outlined_grid_cells
                                    , margin=margin
                                    , draw_scale_matrix = draw_scale_matrix)
    def draw_base_to_surface(self
             , surface:pygame.Surface
             , grid: GridSystem
             , grid_draw_type: GridDrawType = None
             , grid_color: Color = None
             , margin:int=1
             , draw_scale_matrix: np.array = None):
        if grid_draw_type is None:
            grid_draw_type = GridDrawType.BOXES

        if grid_color is None:
            grid_color = Color.BLACK

        if grid_draw_type == GridDrawType.BOXES:
            self._draw_grid_boxes(surface=surface, grid=grid, margin=margin, grid_color=grid_color, draw_scale_matrix = draw_scale_matrix)
        elif grid_draw_type == GridDrawType.LINES:
            self._draw_grid_lines(surface=surface, grid=grid, margin=margin, grid_color=grid_color, draw_scale_matrix = draw_scale_matrix)




    def _draw_outlined_grids(self, surface:pygame.Surface, grid_box_rect: Rectangle, margin=1, outlined_grid_cells: Dict[Vector2, Color] = None, draw_scale_matrix = None):
        if outlined_grid_cells is None or len(outlined_grid_cells) == 0:
            return

        for grid_pos, color in outlined_grid_cells.items():
            if color is None:
                color = Color.YELLOW

            rect = Rectangle(x=(margin + grid_box_rect.width) * grid_pos.x + margin
                             , y=(margin + grid_box_rect.height) * grid_pos.y + margin
                             , height=grid_box_rect.height
                             , width=grid_box_rect.width)
            my_image = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(my_image, color.value, my_image.get_rect(), 3)
            surface.blit(my_image, (rect.x, rect.y))

    def _draw_highlighted_grids(self, surface:pygame.Surface, grid_box_rect: Rectangle, margin=1, highlight_grid_cells: Dict[Vector2, Color] = None, draw_scale_matrix = None):
        if highlight_grid_cells is None or len(highlight_grid_cells) == 0:
            return

        if draw_scale_matrix is None:
            draw_scale_matrix = np.identity(4)

        for grid_pos, color in highlight_grid_cells.items():
            if color is None:
                color = Color.YELLOW
            points = help.scaled_points_of_a_rect(grid_box_rect,
                                                           grid_pos, draw_scale_matrix)[:, :2]

            help.draw_polygon(surface, list(points), color)

            # help.draw_box(surface, Rectangle(x=(margin + grid_box_rect.width) * grid_pos.x + margin
            #                                  , y=(margin + grid_box_rect.height) * grid_pos.y + margin
            #                                  , height=grid_box_rect.height
            #                                  , width=grid_box_rect.width)
            #               , color=color)

    def _draw_grid_boxes(self, surface:pygame.Surface, grid: GridSystem, margin=1, grid_color: Color = None, draw_scale_matrix = None):
        grid_box_rect = self.grid_box_rectangle(surface.get_width(), surface.get_height(), grid, margin)

        if draw_scale_matrix is None:
            draw_scale_matrix = np.identity(4)


        for y in range(0, grid.nRows):
            for x in range(0, grid.nColumns):
                points = help.scaled_points_of_a_rect(grid_box_rect, Vector2(x, y), draw_scale_matrix)[:, :2]
                help.draw_polygon(surface, list(points), grid_color)
                # rect = Rectangle(x=(margin + grid_box_rect.width) * x + margin
                #                                  , y=(margin + grid_box_rect.height) * y + margin
                #                                  , height=grid_box_rect.height
                #                                  , width=grid_box_rect.width)
                # points = [(x[0], x[1], 0, 1) for x in rect.points_tuple()]
                # translated_points = draw_scale_matrix.dot(np.transpose(np.array(points)))
                # help.draw_polygon(surface, translated_points[:, :2], grid_color)

                # help.draw_box(surface, Rectangle(x=(margin + grid_box_rect.width) * x + margin
                #                                  , y=(margin + grid_box_rect.height) * y + margin
                #                                  , height=grid_box_rect.height
                #                                  , width=grid_box_rect.width)
                #               , color=grid_color)


    def _draw_grid_lines(self, surface:pygame.Surface, grid: GridSystem, margin=1, grid_color: Color = None, draw_scale_matrix = None):
        grid_box_rect = self.grid_box_rectangle(surface.get_width(), surface.get_height(), grid, margin)

        if draw_scale_matrix is None:
            draw_scale_matrix = np.identity(4)

        '''Draw each line'''
        for x in range(0, grid.nColumns + 1):
            point_x1 = x * (grid_box_rect.width + margin)
            point_y1 = 0
            start = draw_scale_matrix.dot(np.array([point_x1, point_y1, 0, 1]))
            point_x2 = x * (grid_box_rect.width + margin)
            point_y2 = (grid_box_rect.height + margin) * grid.nRows
            end = draw_scale_matrix.dot(np.array([point_x2, point_y2, 0, 1]))
            _s = tuple(start[:2].astype(int))
            _e = tuple(end[:2].astype(int))
            pygame.draw.aaline(surface, grid_color.value, _s, _e)
        for y in range(0, grid.nRows + 1):
            start = draw_scale_matrix.dot(np.array([0, y * (grid_box_rect.height + margin), 0, 1]))
            end = draw_scale_matrix.dot(np.array([(grid_box_rect.width + margin) * grid.nColumns, y * (grid_box_rect.height + margin), 0, 1]))
            _s = tuple(start[:2])
            _e = tuple(end[:2])
            pygame.draw.aaline(surface, grid_color.value, _s, _e)


        # '''Draw Lines'''
        # vert_lines = []
        # tb = 0
        # for x in range(0, grid.nColumns + 1):
        #     if tb == 0:
        #         #add top then bottom
        #         vert_lines.append((x * (grid_box_rect.width + margin), 0))
        #         vert_lines.append((x * (grid_box_rect.width + margin), (grid_box_rect.height + margin) * grid.nRows))
        #     else:
        #         #add bottom then top
        #         vert_lines.append((x * (grid_box_rect.width + margin), (grid_box_rect.height + margin) * grid.nRows))
        #         vert_lines.append((x * (grid_box_rect.width + margin), 0))
        #     tb = 1 - tb
        #
        # hor_lines = []
        # lr = 0
        # for y in range(0, grid.nRows + 1):
        #     if lr == 0:
        #         #add left then right
        #         hor_lines.append((0, y * (grid_box_rect.height + margin)))
        #         hor_lines.append(((grid_box_rect.width + margin) * grid.nColumns, y * (grid_box_rect.height + margin)))
        #     else:
        #         #add right then left
        #         hor_lines.append(((grid_box_rect.width + margin) * grid.nColumns, y * (grid_box_rect.height + margin)))
        #         hor_lines.append((0, y * (grid_box_rect.height + margin)))
        #     lr = 1 - lr
        #
        # pygame.draw.aalines(surface, grid_color.value, False, vert_lines)
        # pygame.draw.aalines(surface, grid_color.value, False, hor_lines)

    def get_mouse_grid_pos(self, game_area_rect: Rectangle, mouse_pos: Vector2, coord_to_grid_converter: Callable[[Vector2, Rectangle], Vector2], draw_scale_matrix = None):
        if draw_scale_matrix is None:
            draw_scale_matrix = np.identity(4)

        draw_scale_matrix_inv = np.linalg.inv(draw_scale_matrix)

        test = draw_scale_matrix_inv.dot(draw_scale_matrix)
        """Gets the mouse position and converts it to a grid position"""
        mouse_game_area_coord = help.game_area_coords_from_parent_coords(parent_coords=mouse_pos, game_area_surface_rectangle=game_area_rect)
        mouse_over_grid_coords = help.viewport_point_on_plane(mouse_game_area_coord, game_area_rect, draw_scale_matrix, margin=1)
        points = np.array([mouse_over_grid_coords[0], mouse_over_grid_coords[1], mouse_over_grid_coords[2], 1])
        grid_coords = draw_scale_matrix_inv.dot(np.transpose(points))

        # return coord_to_grid_converter(mouse_game_area_coord, game_area_rect)

        return coord_to_grid_converter(Vector2(grid_coords[0], grid_coords[1]), game_area_rect)

    def grid_point_to_viewport_point(self, surface: pygame.Surface, grid, grid_pos: Vector2, grid_point_type: GridPoint = GridPoint.CENTER, margin: int = 1, draw_scale_matrix = None):
        grid_box_rect = self.grid_box_rectangle(surface.get_width(), surface.get_height(), grid, margin)
        grid_box_scaled_points = help.scaled_points_of_a_rect(grid_box_rect, grid_pos=grid_pos, draw_scale_matrix=draw_scale_matrix)

        if grid_point_type == GridPoint.CENTER:
            x = sum(point[0] for point in grid_box_scaled_points)/len(grid_box_scaled_points)
            y = sum(point[1] for point in grid_box_scaled_points) / len(grid_box_scaled_points)
            return Vector2(x, y)
        elif grid_point_type == GridPoint.ORIGIN:
            return Vector2(grid_box_scaled_points[0][0], grid_box_scaled_points[0][1])
        else:
            raise NotImplementedError(f"Unimplemented grid_point_type {grid_point_type}")





