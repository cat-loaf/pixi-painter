from . import UIWidget
from ..Types import RGBA, Vec2d
from pygame import font, Surface, transform


class Label(UIWidget):
    def __init__(
        self,
        text: str,
        position: Vec2d,
        size: Vec2d,
        font: font.Font,
        color: RGBA = (255, 255, 255),
    ):
        self.text = text
        self.font = font
        self.x, self.y = position
        self.size = size
        self.w, self.h = size
        self.color = color
        self.surface = self.font.render(self.text, True, self.color)
        # scale surface to size
        if self.size == (0, 0):
            self.w, self.h = self.surface.get_size()
        self.surface = transform.scale(self.surface, (self.w, self.h))

    def set_text(self, text: str):
        self.text = text
        self.surface = self.font.render(self.text, True, self.color)
        self.surface = transform.scale(self.surface, (self.w, self.h))

    def set_color(self, color: RGBA):
        self.color = color
        self.surface = self.font.render(self.text, True, self.color)
        self.surface = transform.scale(self.surface, (self.w, self.h))

    def set_position(self, position: Vec2d):
        self.x, self.y = position

    def draw(self, surface: Surface):
        surface.blit(self.surface, (self.x, self.y))
