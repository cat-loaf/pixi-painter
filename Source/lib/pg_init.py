import pygame

def initialize_pygame(window_title, width, height):
    """
    Initializes the Pygame library and sets up the display window.
    Args:
        window_title (str): The title of the window.
        width (int): The width of the window in pixels.
        height (int): The height of the window in pixels.
    Returns:
        pygame.Surface: The display surface where all the graphics will be drawn.
    """
    
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(window_title)
    return screen