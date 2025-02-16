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
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()