import pygame
from .pg_init import initialize_pygame

class PygameGlobals:
    def __init__(self):
        # Initialize Pygame
        self.screen_width = 800
        self.screen_height = 600
        self.screen_title = "PixiPainter"
        
        self.screen = initialize_pygame(
            self.screen_title, 
            self.screen_width, 
            self.screen_height
        )
        
        # Colors
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255)
        }
        
        # Fonts
        self.fonts = {
            'default': pygame.font.Font(None, 36),
            'large': pygame.font.Font(None, 72)
        }
        
        # Clock for managing frame rate
        self.clock = pygame.time.Clock()

        # Game states
        self.running = True
        self.paused = False
                
    def quit(self):
        pygame.quit()