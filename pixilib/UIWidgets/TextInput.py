from . import UIWidget
from ..Types import RGBA, Vec2d
from pygame import font, Surface
import pygame
import re


class TextInput(UIWidget):
    def __init__(
        self,
        position: Vec2d,
        size: Vec2d,
        font: font.Font,
        text_color: RGBA = (0, 0, 0),
        box_color: RGBA = (255, 255, 255),
        text: str = "",
        accepted_regex: str = None,
    ):
        self.x, self.y = position
        self.w, self.h = size

        self.text_color = text_color
        self.box_color = box_color

        self.font = font

        self.text = text
        self.text_dirty = True
        self.text_surface = self.font.render(self.text, True, self.text_color)

        self.surface = Surface((self.w, self.h))

        self.accepted_regex = accepted_regex

    def receive_input(self, char: int, unicode: str):
        """Recieve pygame key input

        Args:
            char (str): pygame event.key
            unicode (str): pygame event.unicode
        """
        tmp = self.text
        char: str = pygame.key.name(char)
        self.text_dirty = True
        match char:
            case "backspace":
                if self.text:
                    self.text = self.text[:-1]
            case "return":
                self.text += "\n"
            case "space":
                self.text += " "
            case _:
                if "[" in char and "]" in char:
                    char = char.replace("[", "").replace("]", "")
                if len(char) == 1:
                    if self.accepted_regex:
                        if re.match(self.accepted_regex, unicode):
                            self.text += unicode
                    else:
                        self.text += char
                else:
                    return

        if self.text != tmp:
            self.text_dirty = True

    def set_text(self, text: str):
        if self.text == text:
            return
        self.text_dirty = True
        self.text = text

    def set_color(self, text_color: RGBA, box_color: RGBA):
        self.text_color = text_color
        self.box_color = box_color
        self.surface = self.font.render(self.text, True, self.text_color)

    def set_position(self, position: Vec2d):
        self.x, self.y = position

    def set_size(self, size: Vec2d):
        self.w, self.h = size
        self.surface = Surface((self.w, self.h))

    def draw(self, surface: Surface):
        if self.text_dirty:
            self.text_surface = self.font.render(self.text, True, self.text_color)
            self.text_dirty = False

        # Input box
        surface.fill(self.box_color, (self.x, self.y, self.w, self.h))
        # Text
        surface.blit(self.text_surface, (self.x + 5, self.y + 5))
