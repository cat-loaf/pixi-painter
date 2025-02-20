import pygame

class PaletteIO:
    def __init__(self, file_path):
        self.file_path = file_path
        self.colors = []

    def load(self):
        with open(self.file_path, 'rb') as file:
            while True:
                bytes = file.read(3)
                if not bytes:
                    break
                r, g, b = bytes
                self.colors.append(pygame.Color(r, g, b))
        return self.colors

    def write(self, file_path=None, colors=None):
        if file_path is None:
            file_path = self.file_path
        with open(file_path, 'wb') as file:
            if colors is not None:
                self.colors = colors
            for color in self.colors:
                file.write(bytes([color.r, color.g, color.b]))
