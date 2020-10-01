import pygame
from coopstructs.geometry import Rectangle
from coopgame.colors import Color
from coopstructs.vectors import Vector2
import numpy as np
from typing import List

def mouse_pos_as_vector() -> Vector2:
    """ Get the global coords of the mouse position and convert them to a Vector2 object"""
    pos = pygame.mouse.get_pos()
    return Vector2(pos[0], pos[1])

def draw_box(surface: pygame.Surface, rect: Rectangle, color: Color, width: int = 0):
    pygame.draw.rect(surface, color.value, (rect.x, rect.y, rect.width, rect.height), width)

def draw_polygon(surface: pygame.Surface, points, color: Color, width: int = 0):
    pygame.draw.polygon(surface, color.value, points, width)

def game_area_coords_from_parent_coords(parent_coords: Vector2, game_area_surface_rectangle: Rectangle) -> Vector2:
    """Converts Global Coords into coords on the game area"""
    return Vector2(parent_coords.x - game_area_surface_rectangle.x, parent_coords.y - game_area_surface_rectangle.y)

def scaled_points_of_a_rect(rect, grid_pos: Vector2, draw_scale_matrix = None, margin:int = 1):
    if draw_scale_matrix is None:
        draw_scale_matrix = np.identity(4)

    ''' get the rectangle object representing the grid position that was input'''
    rect = Rectangle(x=(margin + rect.width) * grid_pos.x + margin
                     , y=(margin + rect.height) * grid_pos.y + margin
                     , height=rect.height
                     , width=rect.width)

    '''Convert the rectangle to a list of points at the 4 corners'''
    points = [(x[0], x[1], 0, 1) for x in rect.points_tuple()]

    '''Multiply the points by the transform matrix for drawing'''
    transformed_points = draw_scale_matrix.dot(np.transpose(points)) #Transpose the points to appropriately mutiply

    '''return the x and y position for all points on the rectangle'''
    return np.transpose(transformed_points)[:, :3] #Re-Transpose the points back to remain in a "list of points" format


def scaled_points_of_points(points: List[Vector2], draw_scale_matrix = None):
    if draw_scale_matrix is None:
        draw_scale_matrix = np.identity(4)

    '''Convert the point to a 4-dim point for multiplication'''
    normal_points = [(point.x, point.y, 0, 1) for point in points]

    '''Multiply the points by the transform matrix for drawing'''
    transformed_points = draw_scale_matrix.dot(np.transpose(normal_points))  # Transpose the points to appropriately mutiply

    return np.transpose(transformed_points)[:, :3] #Re-Transpose the points back to remain in a "list of points" format


def viewport_point_on_plane(viewport_point: Vector2, grid_box_rect, draw_scale_matrix = None, margin:int = 1):
    points_on_plane = scaled_points_of_a_rect(grid_box_rect, Vector2(0, 0), draw_scale_matrix, margin = margin)
    point0 = points_on_plane[0]
    point1 = points_on_plane[1]
    point2 = points_on_plane[2]

    vec1 = point0-point1
    vec2 = point2-point1

    normal = np.cross(vec1, vec2)
    a = normal[0]
    b = normal[1]
    c = normal[2]
    d = a * point0[0] + b * point0[1] + c * point0[2]

    z_val = (d - a * viewport_point.x - b * viewport_point.y) / c

    return [viewport_point.x, viewport_point.y, z_val]

def scaled_points_to_normal_points(points, draw_scale_matrix = None):
    if draw_scale_matrix is None:
        draw_scale_matrix = np.identity(4)


    draw_scale_matrix_inv = np.linalg.inv(draw_scale_matrix)

    translated_points = np.array(points)
    normal_points = draw_scale_matrix_inv.dot(np.transpose(translated_points))

    return normal_points
