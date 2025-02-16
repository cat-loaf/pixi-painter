import pygame

def draw_surface(screen, surface, position):
    """
    Draws a surface onto the screen at the specified position.
    Args:
        screen (pygame.Surface): The surface representing the screen or window where the drawing will occur.
        surface (pygame.Surface): The surface to be drawn onto the screen.
        position (tuple): A tuple (x, y) representing the coordinates where the surface will be drawn on the screen.
    Returns:
        None
    """

    screen.blit(surface, position)

def draw_rect(screen, color, rect, width=0):
    """
    Draws a rectangle on the given screen.
    Parameters:
        screen (pygame.Surface): The surface to draw the rectangle on.
        color (tuple): The color of the rectangle, in RGB format.
        rect (tuple): The rectangle's position and size, defined as (x, y, width, height).
        width (int, optional): The width of the rectangle's border. Defaults to 0, which fills the rectangle.
    Returns:
        None
    """

    pygame.draw.rect(screen, color, rect, width)

def draw_circle(screen, color, position, radius, width=0):
    """
    Draws a circle on the given screen.
    Parameters:
        screen (pygame.Surface): The surface to draw the circle on.
        color (tuple): The color of the circle in RGB format.
        position (tuple): The (x, y) position of the center of the circle.
        radius (int): The radius of the circle.
        width (int, optional): The width of the circle's edge. Defaults to 0, which means the circle will be filled.
    Returns:
        None
    """

    pygame.draw.circle(screen, color, position, radius, width)

def draw_line(screen, color, start_pos, end_pos, width=1):
    """
    Draws a line on the given screen.
    Parameters:
        screen (pygame.Surface): The surface to draw the line on.
        color (tuple): The color of the line in RGB format.
        start_pos (tuple): The starting position of the line (x, y).
        end_pos (tuple): The ending position of the line (x, y).
        width (int, optional): The width of the line. Defaults to 1.
    Returns:
     None
    """

    pygame.draw.line(screen, color, start_pos, end_pos, width)