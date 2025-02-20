from enum import Enum
import pygame
import sys, ctypes


class Button:
    def __init__(self, x, y, width, height, color, on_click, get_x=None, get_y=None):
        self.get_x = get_x
        self.x = x
        
        self.get_y = get_y
        self.y = y

        self.color = color

        self.on_click = on_click

        self.rect = pygame.Rect(self.x, self.y, width, height)

    def update_position(self, x=None, y=None):
        if x is None:
            x = self.x
        if y is None:
            y = self.y
        if callable(self.get_x):
            self.x = self.get_x()
            self.rect.x = self.get_x()
        else:
            self.x = x
            self.rect.x = x
        if callable(self.get_y):
            self.y = self.get_y()
            self.rect.y = self.get_y()
        else:
            self.y = y
            self.rect.y = y

    def draw(self, screen):
        self.update_position()
        pygame.draw.rect(screen, self.color, self.rect)
        
class ImageButton(Button):
    def __init__(self, x, y, width, height, image, on_click):
        if callable(x):
            get_x=x
            x=x()
        else:
            get_x=None
        if callable(y):
            get_y=y
            y=y()
        else:
            get_y=None
            
        super().__init__(x, y, width, height, (0,0,0), on_click, get_x, get_y)
        self.image = image
        self.image = pygame.transform.scale(self.image, (width, height))
        
    def draw(self, screen):
        self.update_position()
        screen.blit(self.image, (self.x, self.y))

class ExitButton(ImageButton):
    def __init__(self, x, y, width=24, height=24, func=lambda a : pygame.quit()):
        img = pygame.image.load('./assets/ui/close_button.png')
        super().__init__(x, y, width, height, img, func)

_toggled = False
_maximised_icon     = pygame.image.load('./assets/ui/maximise_button.png')
_maximised_alt_icon = pygame.image.load('./assets/ui/maximise_alt_button.png')
def _toggleFullscreen(btn):
    global _toggled
    if sys.platform == "win32":
        HWND = pygame.display.get_wm_info()['window']
        if not _toggled:
            SW_MAXIMIZE = 3
            ctypes.windll.user32.ShowWindow(HWND, SW_MAXIMIZE)
            btn.image = _maximised_alt_icon
        else:
            SW_RESTORE = 9
            ctypes.windll.user32.ShowWindow(HWND, SW_RESTORE)
            btn.image = _maximised_icon
        _toggled = not _toggled            
            
            
class MaximiseButton(ImageButton):
    def __init__(self, x, y, width=24, height=24, func=_toggleFullscreen):
        img = _maximised_icon
        super().__init__(x, y, width, height, img, func)

class MinimiseButton(ImageButton):
    def __init__(self, x, y, width=24, height=24,func=lambda a : pygame.display.iconify()):
        img = pygame.image.load('./assets/ui/minimise_button.png')
        super().__init__(x, y, width, height, img, func)
        
class PaletteButton(Button):
    def __init__(self, x, y, width, height, on_click, color=(0,0,0)):
        if callable(x):
            get_x=x
            x=x()
        else:
            get_x=None
        if callable(y):
            get_y=y
            y=y()
        else:
            get_y=None
            
        super().__init__(x, y, width, height, color, on_click, get_x, get_y)
        