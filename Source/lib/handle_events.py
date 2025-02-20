import pygame
import sys
from .global_data import PygameGlobals

def handle_events(data: PygameGlobals):
    """
    Handle Pygame events such as quitting the game or pressing the escape key.
    This function processes events from the Pygame event queue. If the user
    attempts to close the window or presses the escape key, the function will
    quit Pygame and exit the program.
    Args:
        data (GlobalData): The global data object containing game state and other
                           relevant information.            
    Events handled:
        QUIT: Close the Pygame window and exit the program.
        KEYDOWN: Check if the escape key is pressed and exit the program if it is.
    """
    events = pygame.event.get()
    data.toolbar.handle_event(events)
    data.palette.handle_event(events)
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                ...
        elif event.type == pygame.WINDOWSIZECHANGED:
            new_width = max(event.x, data.min_width)
            new_height = max(event.y, data.min_height)
            pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            data.toolbar.resize_width(new_width)
            data.screen_width = new_width
            data.screen_height = new_height