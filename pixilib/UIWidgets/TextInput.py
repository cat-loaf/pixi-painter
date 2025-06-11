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
        max_chars: int = -1,
        escape_callback: callable = None,
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
        self.max_chars = max_chars

        self.escape_callback = escape_callback

        self.focused = False

    def set_focused(self, focused: bool):
        self.focused = focused

    def receive_input(self, char: int, unicode: str, tick: int = 0):
        """Recieve pygame key input

        Args:
            char (str): pygame event.key
            unicode (str): pygame event.unicode
        """
        tmp = self.text
        char: str = pygame.key.name(char)
        self.text_dirty = True

        if char == "backspace":
            if self.text:
                self.text = self.text[:-1]
        elif char == "escape":
            if self.escape_callback:
                self.focused = False
                self.escape_callback()
            return

        if self.max_chars > 0 and len(self.text) >= self.max_chars:
            return

        match char:
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

    def draw(self, surface: Surface, tick: int = 0, *args, **kwargs):
        # Input box
        surface.fill(self.box_color, (self.x, self.y, self.w, self.h))
        # Text
        if self.focused:
            # Selection box
            pygame.draw.rect(
                surface,
                (0, 0, 0),
                (self.x + 2, self.y + 2, self.w - 4, self.h - 4),
                1,
            )
            # Text Cursor
            if (tick % 50) < 25:
                cursor_x = self.x + 5 + self.text_surface.get_width()
                cursor_y = self.y + 5 + self.text_surface.get_height()
                pygame.draw.line(
                    surface,
                    self.text_color,
                    (cursor_x, cursor_y),
                    (cursor_x, cursor_y - self.text_surface.get_height()),
                    1,
                )

        if self.text_dirty:
            self.text_surface = self.font.render(self.text, True, self.text_color)

            # Crop text if bigger than (x,y,w,h)
            text_w, text_h = self.text_surface.get_size()
            if text_w > self.w - 10:
                text_w = self.w - 10
            if text_h > self.h - 10:
                text_h = self.h - 10

            # Offset text if past right edge
            text_width = self.text_surface.get_width()
            if text_width > self.w - 10:
                offset = text_width - (self.w - 10)
            else:
                offset = 0

            self.text_surface = self.text_surface.subsurface(
                (offset, 0, text_w, text_h)
            )
            self.text_dirty = False

        surface.blit(self.text_surface, (self.x + 5, self.y + 5))
