import pygame
from .pg_init import initialize_pygame
from .draw import *

class PygameGlobals:
    def __init__(self):
        # Initialize Pygame
        self.screen_width = 800
        self.screen_height = 600
        self.min_width = 400
        self.min_height = 400
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
        
        self.toolbar = None
                
    def quit(self):
        pygame.quit()
        
    def draw(self):
        self.screen.fill(self.colors['white'])
        
        if self.toolbar:
            self.toolbar.draw(self.screen)
        
        pygame.display.flip()
    
    def get_width(self):
        return self.screen_width
    def get_height(self):
        return self.screen_height