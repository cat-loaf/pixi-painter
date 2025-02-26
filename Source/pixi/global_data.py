import pygame, ctypes, sys
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
            'blue': (0, 0, 255),
            'background': pygame.Color("#41444a"),
            'toolbar': pygame.Color("#2e3034")
        }
        
        self.palette_colors = [
            pygame.Color("#ffffff"),
            pygame.Color("#ff0000"),
            pygame.Color("#00ff00"),
            pygame.Color("#0000ff"),
            pygame.Color("#ebedef"),
            pygame.Color("#f78d05"),
            pygame.Color("#f44242"),
            pygame.Color("#f4428a"),
            pygame.Color("#f442f4"),
            pygame.Color("#f4a2f4"),
            pygame.Color("#f4f2f4"),
            pygame.Color("#f4f2f2")
        ]
        
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
        self.palette = None
        self.selected_color = 0
                
    def quit(self):
        pygame.quit()
        
    def draw(self):
        self.screen.fill(self.colors['background'])
        
        if self.toolbar:
            self.toolbar.draw(self.screen)
        
        if self.palette:
            self.palette.draw(self.screen)
        
        pygame.display.flip()
    
    def get_width(self):
        return self.screen_width
    def get_height(self):
        return self.screen_height