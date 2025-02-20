from ..global_data import PygameGlobals
from ..ui.buttons import *

class Palette:
    def __init__(self, x, y, w, h, colors, data: PygameGlobals, padding=2):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.padding = padding
        self.colors = colors
        self.data = data
        self.buttons = []
        self.selected = None
        self._generate_buttons()

    def _generate_buttons(self):
        self.buttons=[]
        for i, color in enumerate(self.colors):
            self.buttons.append(
                PaletteButton(
                    self.x + self.padding,
                    (self.padding+self.y) + (i*self.padding) + (i*self.h),
                    self.w,
                    self.h,
                    on_click=lambda c: self.select(c),
                    color=color,
                )
            )
    
    def select(self, color):
        index=0
        for col in self.colors:
            if col == color:
                index = self.colors.index(col)
        self.selected = self.buttons[index]
        self.data.selected_color = self.buttons[index]
        print(self.selected.color)        
    
    def draw(self, screen):
        backing = pygame.Rect(self.x, self.y, self.w + self.padding * 2, self.h * len(self.colors) + self.padding * 2)
        pygame.draw.rect(screen, self.data.colors['toolbar'], backing)
        for button in self.buttons:
            button.draw(screen)
            
    def handle_event(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button.rect.collidepoint(event.pos):
                        self.select(button.color)
                        break