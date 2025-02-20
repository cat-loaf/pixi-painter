import pygame
from ..global_data import PygameGlobals

class Toolbar:    
    def __init__(self, x, y, width, height, color, data: PygameGlobals):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.buttons = []
        self.data = data

    def add_button(self, button):
        self.buttons.append(button)
        return self
    def add_buttons(self, buttons):
        for button in buttons:
            self.add_button(button)
        return self

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        for button in self.buttons:
            button.draw(screen)

    def handle_event(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    for button in self.buttons:
                        if button.rect.collidepoint(event.pos):
                            button.on_click(button)
    def resize_width(self, new_width):
        self.rect.width = new_width
